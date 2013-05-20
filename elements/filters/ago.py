from datetime import datetime

from django import template
from django.utils import timezone
from django.utils.translation import ungettext_lazy
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter(name='ago')
def ago(last_update, d=None):

    d =  datetime.utcnow() - last_update
    hours = d.seconds / 3600
    minutes = d.seconds / 60
    if d.days >= 1:
        ago = ungettext_lazy(
                            '%(count)i day ago',
                            '%(count)i days ago',
                            d.days) % {'count': d.days}
    elif hours >= 1 and d.days >= 0:
        ago = ungettext_lazy(
                            '%(count)i hour ago',
                            '%(count)i hours ago',
                            hours) % {'count': hours}
    elif minutes >= 1 and d.days >= 0:
        ago = ungettext_lazy(
                            '%(count)i minute ago',
                            '%(count)i minutes ago',
                            minutes) % {'count': minutes}
    else:
        ago = _(u'few seconds ago')

    return ago

register.filter('ago', ago)
