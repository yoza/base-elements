(function() {
    var jQuery = jQuery || $ || django.jQuery;
    jQuery(function ($) {
        var change_content = $('#content-main');

        // Add a page id to the list of expanded pages
        function add_expanded(id) {
            var expanded = get_expanded();
            if ($.inArray(id, expanded) == -1) {
                expanded.push(id);
                set_expanded(expanded);
            }
        }

        // Remove a page id from the list of expanded pages
        function rem_expanded(id) {
            var expanded = get_expanded();
            var index = $.inArray(id, expanded);
            if (index != -1) {
                // The following code is based on J. Resig's optimized array remove
                var rest = expanded.slice(index+1);
                expanded.length = index;
                expanded.push.apply(expanded, rest);
                set_expanded(expanded);
            }
        }

        // Get the list of expanded page ids from the cookie
        function get_expanded() {
            var cookie = pages.cookie('inline_expanded');
            return cookie ? cookie.split(',') : [];
        }

        // Save the list of expanded page ids to the cookie
        function set_expanded(array) {
            pages.cookie('inline_expanded', array.join(','), { 'expires': 14 }); // expires after 12 days
        }

        // let's start event delegation
        change_content.click(function (e) {
            var target = $(e.target);
            var link = target.closest('a').andSelf().filter('a');

            if (!target.hasClass('help') && link.length) {
                // Expand or collapse pages
                if (link.hasClass('expand-collapse')) {
                    var id = link.attr('id');
                    if (link.toggleClass('expanded').hasClass('expanded')) {
                        $(link).parent().parent().find('div.closed').css('display','block');
                    } else {
                        $(link).parent().parent().find('div.closed').css('display','none');
                    }
                    return false;
                }
            }
        });
    });
})(django ? django.jQuery : jQuery);
