"""
common filters
"""

import re
try:
    import markdown2 as markdown
except ImportError:
    import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linkify(value, arg=''):
    """
    return anhor with class

    """

    regex = re.compile(r'(([a-zA-Z]+)://[^ \t\n\r]+)', re.MULTILINE)

    def _spacify(hrf, chars=40):
        """
        urltext space
        """
        if len(hrf) <= chars:
            return hrf
        for k in range(len(hrf) / chars):
            pos = (k + 1) * chars
            hrf = hrf[0:pos] + ' ' + hrf[pos:]
        return hrf

    def _replace(match):
        """
        result of urlify
        """
        href = match.group(0)
        cls = arg and (' class="%s"' % arg) or ''
        return '<a target="_blank" href="%s"%s>%s</a>&nbsp;' % (href,
                                                                cls,
                                                                _spacify(href))
    return regex.sub(_replace, value)


@register.filter(is_safe=True)
@stringfilter
def mark_down(value):
    """
    markdown filter
    """

    return mark_safe(markdown.markdown(force_text(value)))

register.filter('mark_down', mark_down)
