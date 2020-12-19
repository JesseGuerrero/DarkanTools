/* Christmas
* 1. Christmas light string over Darkan tools picture canva, switching every 3 seconds
* 2. Santa hat on skills icon
* 3. Highlighted color for navbar is red
*
* Add New Years later + make this a general holiday thing
* */
var i = 1;
setInterval(function(){
    if(i==1)
        i=2
    else
        i=1
    document.getElementById("brand").src = '/images/christmas_title'+i+'.png';
}, 3000);