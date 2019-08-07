document.addEventListener(
    "DOMContentLoaded",
    function() {
        var list = document.getElementById('assignment-list');
        if (list != null) {
            var buttons = document.getElementsByClassName('xp-switch');
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
            
            buttons = document.getElementsByClassName('percentage-switch');
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

        let elements = document.querySelectorAll('.tooltipped');
        elements.forEach(
            function (element) {
                let name = element.getAttribute("data-name");
                let description = element.getAttribute("data-description");
                let percentage = element.getAttribute("data-name");
                let icon = element.getAttribute("data-icon");
                let options = {
                    enterDelay: 0,
                    margin: 3,
                    html:
                        `<dl class='badge-description'>
                            <dt>
                                <span>${name}</span>
                                <img class='badge-image primary-color' src='${icon}'>
                            </dt>
                            <dd>${description}</dd>
                        </dl>`
                }
                let tooltip = M.Tooltip.init(element, options);
                element.onclick = function () {
                    if (tooltip.isOpen) {
                        tooltip.close();
                    } else {
                        tooltip.open();
                    }
                    
                }
            }
        );

        var dropdownButtons = document.querySelectorAll('.dropdown-trigger');
        M.Dropdown.init(dropdownButtons, {coverTrigger: false});
        
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