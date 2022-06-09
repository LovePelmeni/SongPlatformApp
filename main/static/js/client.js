var group_id = document.getElementById('group_id').value;
var nickname = document.getElementById('username').value;

var jid = document.getElementById('jid').value;
var password = document.getElementById('password').value;

var roomJid = String('group' + group_id + '@conference.localhost');
var serverURL = 'http://localhost:7070/http-bind/';
var connection = new Strophe.Connection(serverURL);
connection.connect(jid, password, CheckConnection);

// handlers:

function getJwtCookie(){

    for (var cookie in document.cookie.split('; ')){
        if (cookie.split('=')[0] == 'jwt-token'){
            return cookie('=')[1]
        } else{
            continue
        }
    }
}

function GetQueryset(group_id){

    var url = new URL("http://localhost:8090/get/message/queryset/");
    url.searchParams.append('group_id', group_id);

   var queryset;
   $.ajax({
        url: url,
        type: "GET",
        async: false,
        headers : {
            'Authorization': getJwtCookie(),
        },
        success: function(response){
            queryset = response.msg_queryset;
        },
        error: function(error){
            console.log('error has occurred...', error);
        }
    });
   return queryset;
}


var feed_queryset = GetQueryset(group_id);
console.log(feed_queryset);




function GetFile(file_id, url){
    try{
    request = new XMLHttpRequest();
    request.open('GET', url, false);
    request.send();
    return request.responseText.file;
    }catch(e){throw e};
}



function HandleFileMessage(message){

    image_api_url = new URL('http://localhost:8000/get/image/');
    video_api_url = new URL('http://localhost:8000/get/video/');

    try{
    file_id = JSON.parse(message).file_id;
    file_type = JSON.parse(message).file_type;

    if (file_type == 'image'){
        file = GetFile(file_id, url);
        console.log('image file obtained...', file);
    } else {
        file = GetFile(file_id, video_api_url);
        console.log('video file obtained...', file);
    }
    console.log('file has been received... with id', message);
    return true;

    }catch(e){
        console.log('file not found...');
        return true;
    }
}


function HandleAddUser(event){
    console.log('user added..');
    return true;
}


function HandleRemoveUser(event){
    console.log('user removed...');
    return true;
}

function HandleBanUser(event){
    console.log('ban event has been received...');
    var banURL = new URL("http://localhost:8000/get/ban/page/");
    return window.location.replace(banURL);
}

function HandleCreateMessage(message){
    // some logic of showing out messages....
    console.log('one more message, ', message);
    return true;
}


function HandleEditMessage(message){
    console.log('edited message:', message)
    return true;
}


function HandleDeleteMessage(message){
    console.log('deleted message:', message);
    return true;
}


function HandleExceptions(exception){
    console.log('error has occurred', exception);
    return true;
}


// connection methods:


function CheckConnection(status){

  if (status == Strophe.Status.DISCONNECTED){
        try {
            connection.restore(jid, CheckConnection);
            console.log('connection restored...')
        }
        catch(e) {
            if (e.name !== "StropheSessionError") { throw(e); }
            console.log('reconnection...');
        }
  } else {

    if (status == Strophe.Status.CONNECTED) {

        connection.send($pres({from: jid}).tree());
        console.log('connected successfully...');

        connection.addHandler(HandleCreateMessage, null, "message", "groupchat");
        connection.addHandler(HandleDeleteMessage, 'xxxx:delete_message', "iq", null, null, null, null);
        connection.addHandler(HandleEditMessage, 'xxxx:edit_message', "iq", null, null, null, null);

        connection.addHandler(HandleExceptions, "xxxx:error", "iq", null, null, null, null);
        connection.addHandler(HandleBanUser, "xxxx:ban", "iq", null, null, null);

   try {
       JoinGroup(nickname=nickname, group_id);
       console.log('joined group...');
   }
   catch(e){
    console.log('not implemented...', e);
   }
} else {
    console.log('could not connect..');
}}}


function JoinGroup(){

    connection.sendPresence($pres({
        from: jid,
        to: roomJid + '/' + nickname
    }).tree());
}


function LeaveGroup(){

    var redirectURL = new URL('http://localhost:8000/');
    redirectURL.searchParams.append('user_id', user_id);
    console.log('leave group...');
    connection.disconnect();
    return window.location.replace(redirectURL);
}



function EditMessage(message_id, edit_data, group_id){

    editFromDatabase(message_id, edit_data, group_id);
    var stanza = EditMessageStanza(group_id, edit_data, message_id);
    connection.sendIQ(stanza);


    function EditMessageStanza(group_id, edit_data, message_id){

        var edit_obj = {'edit_data': edit_data, 'message_id': message_id, 'nickname': nickname}
        var iq = $iq({type: 'set', to: 'group' + group_id + '@conference.localhost', xmlns: "xxxx:edit_message"
        }).c('edit_message').c('data').t(JSON.stringify(edit_obj));
        return iq;
    }

    function editFromDatabase(message_id, edit_data, group_id){
    try{
        var url = new URL('http://localhost:8090/edit/message');
        url.searchParams.append('message_id', message_id);
        url.searchParams.append('group_id', group_id)

       $.ajax({
            url: url,
            type: "PUT",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: JSON.stringify(edit_data),
            async: false,
            success: function(response){
                console.log('edited successfully.', response);
            },
            error: function(error){
                console.log('error has occurred...', error);
            }
        });
    }catch(e){
        console.log('could not send request for editing message...', e)
    }
}}



function DeleteMessage(group_id, message_id){

    deleteFromDatabase(group_id, message_id);
    var stanza = DeleteMessageStanza(message_id, group_id);
    connection.sendIQ(stanza);

    function DeleteMessageStanza(message_id, group_id){
        var obj = {'message_id': message_id, 'group_id': group_id, 'nickname': nickname}
        var iq = $iq({type: 'set', to: 'group' + group_id + '@conference.localhost', xmlns: 'xxxx:delete_message'
        }).c('delete_message').c('data').t(JSON.stringify(obj));
        return iq;
    }

    function deleteFromDatabase(group_id, message_id){
    try{
        var url = new URL('http://localhost:8090/delete/message');
        url.searchParams.append('message_id', message_id);
        url.searchParams.append('group_id', group_id)

        $.ajax({
            url: url,
            type: "DELETE",
            async: false,
            success: function(response){
                console.log('deleted successfully')
            },
            error: function(error){
                console.log('error has occurred...', error);
            }
        });
    }catch(e){
        console.log('could not send request for deleting message...', e)
    }
}}



editForm.addEventListener('submit', function(event){
    editForm.preventDefault();
    try{
        message_obj = $(this).serialize();
        EditMessage(group_id, message_obj.message_id, message_obj);
    }catch(e){
        console.log('could not edit message');
    }
});


banBtn.addEventListener('click', function(event){

    function SendBanEvent(connection, jid){
    var stanza = $iq({type: 'set', to: jid, xmlns: "ban_user"}).c('data');
    connection.send(stanza);
    console.log('ban event has been sended..')
    }

    function BanUser(username, jid){
        var api_url = new URL("http://localhost:8000/ban/or/unlock/user/");
        api_url.searchParams.append('username', username);
        $.ajax({
            url: api_url,
            type: 'POST',
            async: false,

            success: function(response){
                if (response.status_code in (200, 201)){
                    return SendBanEvent(jid);
                } else{
                    console.log('could not ban user..')
                }
            },
            error: function(error){
                console.log('exception has been raised...', error);
            }
        });
    }

    var target_username, target_jid = banBtn.value.split('#');
    if (target_jid == jid){
        console.log('you cannot ban yourself...');
    }
    BanUser(username, jid);
    console.log('ban request has been sended...')
});

deleteBtn.addEventListener('submit', function(event){
    deleteBtn.preventDefault();
    try{
    message_id = document.getElementById('deleteBtn').value[0];
    DeleteMessage(group_id, message_id);
    } catch(e){
        console.log('message could not be deleted...');
    }
});



messageForm.addEventListener('submit', function(event){
    window.preventDefault();
    try{
    message_obj = $(this).serialize();
    SendMessage(message_obj);
    } catch(e){
        console.log('could not save message to database...');
    }
});




btn.addEventListener('click', function(event){

    var edit_data = {'message': 'New Message'}
    var message_id = SendMessage({'message': 'Hi There'});
    console.log('message_id-', message_id);
    EditMessage(message_id, edit_data, group_id);
    DeleteMessage(group_id, message_id);

});




function SendMessage(message_obj){

    var message_id = saveToDatabase(message_obj);
    message_obj.message_id = message_id;
    var message = $msg({id: "message-id", to: 'group' + String(group_id) + '@conference.localhost',
    from: jid, type: 'groupchat', }).c("body", {xmlns: "http://jabber.org/protocol/muc"}).t(JSON.stringify(message_obj));
    connection.send(message.tree());
    console.log('sended create event.');

    function saveToDatabase(group_id, message_obj, jid){
    try{
        var url = new URL('http://localhost:8090/create/message/');
        var payload = {'group_id': group_id, 'message': message_obj, 'author_jid': jid}
        var message_id;
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(payload),
            async: false,
            success: function(response){
                message_id = JSON.parse(response).message_id;
            },
            error: function(error){
                console.log('error has occurred...', error);
            }
        });
        console.log('obtained...', message_id);
        return message_id;

    }catch(e){
        console.log('could not send request for creating new message...', e)
    }}
    return message_id;
}

