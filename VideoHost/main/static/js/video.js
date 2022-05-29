function StreamVideo(){
    var url = new URL('http://localhost:8000/stream/video/');
    var request = new XMLHttpRequest();
    request.open('GET', url, false);
    request.setRequestHeader();
    request.send(null);
    // some logic of catching streaming chunks and put it into video tag
}