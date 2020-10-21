function LikeCheck(e) {
    var like_block = document.getElementById(e);
    var like_background = like_block.firstElementChild;
    var like_index = like_block.lastElementChild;
    var csrf_token =  document.getElementsByName('csrfmiddlewaretoken');

    $.ajax({
        type: "GET",
        // url: "{% url 'like_check_url' %}",
        url: "/likes_and_statistics/like_check/",
        contentType: "application/x-www-form-urlencoded;charset=UTF-8",
        headers: {
            "X-CSRFToken": csrf_token[0].value,
        },

        data: {
            slug: e,
        },

        success: function(data) {
          $(like_index).html(data.like_updated);
            if (data.like_checked) {
              $(like_background).animate({
                backgroundPositionY: "-26px",
              });
            }
            
            else {
              $(like_background).animate({
                backgroundPositionY: "0px",
              });
            }
        },
    });
  }
