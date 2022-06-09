function GetAllGroupMembers(){
    var url = new URL('http://127.0.0.1:8000/get/all/group/members/');
    url.searchParams.append('group_name', url, false);

    request = new XMLHttpRequest();
    request.open('GET', url, false);
    request.send(null);
}

function EditGroup(group, edit_data){

    data = new FormData(edit_data);
    post_url = new URL('http://127.0.0.1:8000/edit/group/');
    post_url.searchParams.append('group_name', group.group_name);

    request = new XMLHttpRequest();
    request.open('POST', url, false);

    request.setRequestHeader('Last-Modified', group.last_updated);
    request.setRequestHeader('Cors-Allow-Origin', window.domain);
    request.send(edit_data);

    if (request.responseText == 412){
        console.log('resending request cuz returned 412 status');
        return CheckForIdentityGroup();
    }
}

function CheckForIdentityGroup(group=null){

    var group_obj = document.getElementById('group_obj').value;
    if (group != null){
        group_obj = group;
    }
    var url = new URL('http://127.0.0.1:8090/get/group/');
    url.searchParams.append('group_name', group.group_name);

    var request = new XMLHttpRequest();
    request.open('GET', url, false);

    request.setRequestHeader('Last-Modified', group.last_updated);
    request.setRequestHeader('If-Match', group.etag);
    request.send(null);

    if (request.responseCode == 304){
        console.log('data is modified...');
        return EditGroup(group);
    }
}
