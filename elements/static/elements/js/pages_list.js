/* Initialization of the change_list page - this script is run once everything is ready. */

(function() {
    var jQuery = jQuery || $ || django.jQuery;
    jQuery(function ($) {
        var changelist = $('#navigation');

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
            var cookie = pages.cookie('tree_expanded');
            return cookie ? cookie.split(',') : [];
        }

        // Save the list of expanded page ids to the cookie
        function set_expanded(array) {
            pages.cookie('tree_expanded', array.join(','), { 'expires': 14 }); // expires after 12 days
        }

        // let's start event delegation
        changelist.click(function (e) {
            var target = $(e.target);
            var link = target.closest('a').andSelf().filter('a');

            if (!target.hasClass('help') && link.length) {
                // Expand or collapse pages
                if (link.hasClass('expand-collapse')) {
                    var id = link.attr('id').substring(1);
                    if (link.toggleClass('expanded').hasClass('expanded')) {
                        $(link).parent().parent().find('ul:first').css('display','block');
                        add_expanded(id);
                    } else {
                        $(link).parent().parent().find('ul:first').css('display','none');
                        rem_expanded(id);
                    }
                    return false;
                }
            }
        });
    });
}());
