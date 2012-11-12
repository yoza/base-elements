(function($) {
    clearInput = function(form_id, field_id, label) {
        var label = label;
        var field = $(field_id);

        $(document).ready(function() {
            if (!field.val() || field.val() == label) {
                field.val(label).addClass("empty");
            }
        });
        $(form_id).submit(function() {
            if (field.val() == label) {
                field.val("");
            }
        });
        field.focus(function() {
            if ($(this).val() == label) {
                $(this).val("").removeClass("empty");
            }
        });
        field.blur(function() {
            if ($(this).val() == "") {
                $(field).val(label).addClass("empty");
            }
        });

        return false;
    }

    $.intValue = function(v) {
        v = parseInt(v);
        return isNaN(v) ? 0 : v;
    }

    getParam = function(key) {
        var value=RegExp(""+key+"[^&]+").exec(window.location.search);
        return unescape(!!value ? value.toString().replace(/^[^=]+/,"").replace("=","") : "");
    };


})(jQuery.noConflict());
