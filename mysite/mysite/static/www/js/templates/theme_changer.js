function darkThemeEnable(style_path) {
    var open_theme = document.getElementById('openDarkTheme');
    var current_theme = open_theme.classList.item(1);

    console.log(open_theme, current_theme);
    
    if (current_theme != null ) {

        $.ajax({
            type: "GET",
            url: "/blog/change_theme/",
            contentType: "application/x-www-form-urlencoded;charset=UTF-8",

            data: {
                current_theme: current_theme,
            },

            success: function(data) {
                var tagHead = document.getElementsByTagName('head');

                if (data.response_theme_key == 'dark_theme') {
                    open_theme.classList.replace('original-theme', 'dark-theme');
                    var tagLink = document.createElement('link');
                    tagLink.rel = 'stylesheet';
                    tagLink.href = style_path;
                    tagLink.type = 'text/css';
                    
                    tagHead[0].appendChild(tagLink);
                }

                if (data.response_theme_key == 'original_theme') {
                    open_theme.classList.replace('dark-theme', 'original-theme');
                    var last_link_child = tagHead[0].lastElementChild.remove();
                }

            },
            });
    }
}