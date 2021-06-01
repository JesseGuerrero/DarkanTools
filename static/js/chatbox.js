const socket = io();
socket.on('server_message', (data) => {
    let e = document.createElement('p');

    let sp = document.createElement('span');
    sp.innerHTML = data.nickname;
    e.appendChild(sp);
    e.innerHTML = e.innerHTML+'>> '+data.message;
    if(document.getElementById('message-box').children.length>20){
        document.getElementById('message-box').removeChild(document.getElementById('message-box').children[0]);
    }
    document.getElementById('message-box').appendChild(e);

    document.getElementById('message-box').scroll(0, document.getElementById('message-box').scrollHeight);
});
function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function sendMessage(){
    socket.emit('client_message', {'nickname': htmlEntities(document.getElementById('nickname-input').value), 'message':  htmlEntities(document.getElementById('message-input').value)});
    document.getElementById('message-input').value = '';
}
function isPressingEnter(e){
    let k;
    if(window.event){
        k = e.keyCode;
        if(k===13){
            sendMessage();
        }
    }else if(e.which){
        k = e.which;
        if(k===13){
            sendMessage();
        }
    }
}