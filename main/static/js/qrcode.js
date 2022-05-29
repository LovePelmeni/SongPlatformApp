// firstly scan image, then converts to jpg, then sends
GetQrCode();
var redirectURL = new URL('http://localhost:8000/get/user/profile/');

function stringToBytes ( str ) {
  var ch, st, re = [];
  for (var i = 0; i < str.length; i++ ) {
    ch = str.charCodeAt(i);
    st = [];
    do {
      st.push( ch & 0xFF );
      ch = ch >> 8;
    }
    while ( ch );
    re = re.concat( st.reverse() );
  }
  return re;
}

function ShowQrCodeImageFile(bytesData){
    array = stringToBytes(bytesData);
    file_reader = new FileReader(bytesData);
    console.log(file_reader.result);

    image_field = document.getElementById('image-field'); // need to create this field...
    file_reader.readAsDataURL(new Blob(array, {type: "image/png"}));
}

///*
//function AuthSessionData(data){
//    url = new URL("http://localhost:8000/auth/session/");
//    request = new XMLHttpRequest();
//    request.open('POST', url, false);
//    request.send(data);
//}
//*/

//function ListenForResponse(ip_address){
//
//    websocket_url = new URL('ws://localhost:8000/share/session/' + encodeURIComponent(ip_address) + '/');
//    socket = new WebSocket(websocket_url);
//
//    socket.onopen = function(event){
//        console.log('listen connection opened..')
//    }
//    socket.onmessage = function(data){
//
//        console.log('response message has occurred...')
//        decoded_data = JSON.parse(data);
//        AuthSessionData(decoded_data);
//        socket.close();
//        return window.replace(redirectURL);
//    }
//    socket.onclose = function(){
//        console.log('session closed...')
//    }
//    socket.onerror = function(error){
//        console.log('some error occurred...', error)
//    }
//}

//function GetUserIpAddress(){
//    console.log('ip address has been obtained...');
//    url = new URL("http://ipinfo.io/json/");
//    request = new XMLHttpRequest(url);
//    request.open('GET', url, false);
//    request.send(null);
//    return JSON.parse(request.responseText).ip;
//}

function GetQrCode(){
    var url = new URL('http://localhost:8000/create/qr/code/');
    image_field = document.getElementById('image-field');
    request = new XMLHttpRequest();
    request.open('GET', url, false);

    request.send(null);
    array = JSON.parse(request.responseText);
    source_url = 'data:image/bmp;base64,' + btoa(String.fromCharCode.apply(null, new Uint8Array(array)));

    image_field.src = source_url;
//    return ListenForResponse(ip_address);
}


