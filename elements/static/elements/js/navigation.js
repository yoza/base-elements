if (!jQuery) {
    jQuery = django.jQuery;
}

var NavigationNested = Nested.extend({
    start: function(event) {
        event = new Event(event);
        if (event.target.nodeName == 'SPAN' && event.target.className == 'movespan') {
            this.parent(event);
        }
    }
});

window.addEvent('domready',function(){

// Window.onDomReady(function(){
    var sortIt = new NavigationNested('navigation', {
        collapse: false,
        onStart: function(el) {
            el.addClass('drag');
        },
        onComplete: function(el) {
            el.removeClass('drag');
            var newSerialized = sortIt.serialize();
            if (Json.toString(sortIt.lastSerialized) != Json.toString(newSerialized)) {
                el.addClass('changed');
                jQuery('li.changed').find("input.action-select").attr('checked', true);
            }
            this.lastSerialized = newSerialized;
        }
    });
    var down_date;
    var form = $('navigation-form');
    form.addEvent('submit', function() {
        form.adopt(new Element('input').setProperties({'type': 'hidden', 'name': 'navigation', 'value':Json.toString(sortIt.lastSerialized)}));
    });
    $$('#navigation .toolbox').addEvent('click', function(event) {
        //event.stop();
        //event.preventDefault();
        //event.stopPropagation();
    });
    $$('#navigation li>a').addEvent('mousedown', function(event) {
        down_date = new Date().getTime();
    });
    $$('#navigation li>a').addEvent('click', function(event) {
        var delta = (new Date()-down_date);
        if (delta > 400)
            event.preventDefault();
    });
    sortIt.lastSerialized = sortIt.serialize();
});


