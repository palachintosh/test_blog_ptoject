function LikeCounter(e) {
    var like_block = document.getElementById(e);
    var like_background = like_block.firstElementChild;
    var like_index = like_block.lastElementChild;
    var csrf_token =  document.getElementsByName('csrfmiddlewaretoken');

    console.log(e, csrf_token[0].value, 'index: ' + like_index.textContent)
    // console.log(like_block, like_index, like_background.textContent);

    $.ajax({
        type: "POST",
        // url: "{% url 'like_response_url' %}",
        url: "/likes_and_statistics/like_response/",
        contentType: "application/x-www-form-urlencoded;charset=UTF-8",
        headers: {"X-CSRFToken": csrf_token[0].value},
    

        data: {
            like_index: like_index.textContent,
            slug: e,
        },

        success: function(data) {
            $(like_index).html(data.like_updated);
              if (data.remove_like) {
                $(like_background).animate({
                  backgroundPositionY: "0px",
                });
              }
              else {
                $(like_background).animate({
                  backgroundPositionY: "-26px",
              });
              }
            },

        error: function(data) {
          alert("Oooops, something goes wrong. Please, reload page and try again!");
        }
        


    });
  }