"""
Simple tags for admin
"""

from django.conf import settings
from django import template
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


register = template.Library()

@register.simple_tag
def fb_admin_tag():
    fbtag = ""
    if getattr(settings, 'FILEBROWSER_ADMIN', False):
        url = reverse('filebrowser-index')
        fbtag = u'<div class="module"><table>'\
                u'<caption>%s</caption>' % unicode(_("File-Browser"))
        fbtag += u'<tr class="row2"><th scope="row">'\
                 u'<a href="%s">%s</a>' % (url, unicode(_("File-Browser")))
        fbtag += u'</th><td> </td><td> </td></tr></table></div>'
    return fbtag
