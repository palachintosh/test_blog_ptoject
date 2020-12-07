//promise ============================
function spanChenger (rt, rotation_var, unset_content) {
    if(unset_content == 1) {
        $('.container-menu').hide("fast");
    }
    rt[0].firstElementChild.textContent = rotation_var;
}

//Open ============================
function OpenMenu () {
    var rt = document.getElementsByClassName("container-menu");
    let rotation_var = Number(rt[0].firstElementChild.textContent);

    $('.container-menu').animate({  borderSpacing: rotation_var },
    {
        step: function(now,fx) { 
            $(this).css('-moz-transform', 'rotate('+now+'deg)');
            $(this).css('transform', 'rotate('+now+'deg)');
            $(this).css('-webkit-transform', 'rotate('+now+'deg)');
            $(this).css('display', 'block');
        },
    easing: 'easeOutBounce', 
    },1000,).promise(spanChenger(rt, rotation_var=0));
}

//close ============================
function CloseMenu () {
    var rt = document.getElementsByClassName("container-menu");
    let rotation_var = Number(rt[0].firstElementChild.textContent);

    $('.container-menu').animate({  borderSpacing: rotation_var },
    {
        step: function(now,fx) { 
            $(this).css('-moz-transform', 'rotate('+now+'deg)');
            $(this).css('transform', 'rotate('+now+'deg)');
            $(this).css('-webkit-transform', 'rotate('+now+'deg)');
        },
    easing: 'linear', 
    },1000,).promise(spanChenger(rt, rotation_var=90, unset_content=1));
}