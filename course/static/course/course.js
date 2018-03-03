document.addEventListener(
    "DOMContentLoaded",
    function() {
        var list = document.getElementById('assignment-list');
        if (list != null) {
            var buttons = document.getElementsByClassName('change-to-xp');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].addEventListener(
                    'click',
                    function (event)
                    {
                        list.classList.remove('show-percentage');
                        event.preventDefault();
                    },
                    true
                );
            }
            
            buttons = document.getElementsByClassName('change-to-percentage');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].addEventListener(
                    'click',
                    function (event)
                    {
                        list.classList.add('show-percentage');
                        event.preventDefault();
                    },
                    true
                );
            }
        }
        
        var showMore = document.getElementById('show-more-ranking');
        var ranking = document.getElementById('class-ranking');
        if (showMore != null && ranking != null) {
            showMore.addEventListener(
                'click',
                function (event)
                {
                    ranking.classList.add('expanded');
                    event.preventDefault();
                },
                true
            );
        }
    }
);