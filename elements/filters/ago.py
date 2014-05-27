"""
ago filter
"""

from datetime import datetime

from django import template
from django.utils.translation import ungettext_lazy
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter(name='ago')
def ago(last_update, dit=None):
    """
    ago filter
    """
    dit = datetime.utcnow() - last_update
    hours = dit.seconds / 3600
    minutes = dit.seconds / 60
    if dit.days >= 1:
        ego = ungettext_lazy('%(count)i day ago',
                             '%(count)i days ago',
                             dit.days) % {'count': dit.days}
    elif hours >= 1 and dit.days >= 0:
        ego = ungettext_lazy('%(count)i hour ago',
                             '%(count)i hours ago',
                             hours) % {'count': hours}
    elif minutes >= 1 and dit.days >= 0:
        ego = ungettext_lazy('%(count)i minute ago',
                             '%(count)i minutes ago',
                             minutes) % {'count': minutes}
    else:
        ego = _(u'few seconds ago')

    return ego

register.filter('ago', ago)
