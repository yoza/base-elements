import re
import urllib
import hashlib
from django.conf import settings
from elements.models import SiteParams
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def logo_tag(context):
    logo = ""
    site_logo = getattr(settings, 'LOGO_IMAGE', ("maipage/img/logo.png",
                                                 "0,0,85,85"))
    try:
        params = SiteParams.objects.language().get(site__id=settings.SITE_ID)
        tags = 'span p br div sub sup a'
        tags = [re.escape(tag) for tag in tags.split()]
        tags_re = u'(%s)' % u'|'.join(tags)
        starttag_re = re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
        endtag_re = re.compile(u'</%s>' % tags_re)
        value = starttag_re.sub(u' - ', params.title)
        value = endtag_re.sub(u'', value)
        logo = u'<div class="logo_layer">\
                    <img usemap ="#logo_map" src="%s" alt="%s" id="img_logo"/>\
                    <map id ="logo_map" name="logo_map">\
                        <area href="/" target="_self" id="area_logo_map" \
                              shape ="rect" coords ="%s" alt="%s"/>\
                    </map>\
                </div>' % (site_logo[0], value, site_logo[1], value)

    except SiteParams.DoesNotExist:
        pass

    return  mark_safe(logo)
register.simple_tag(takes_context=True)(logo_tag)


def site_param(context, param, tags=""):

    try:
        entry = SiteParams.objects.language().values(param).get(site__id=settings.SITE_ID)
        if tags:
            tags = [re.escape(tag) for tag in tags.split()]
            tags_re = u'(%s)' % u'|'.join(tags)
            starttag_re = re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
            endtag_re = re.compile(u'</%s>' % tags_re)
            value = starttag_re.sub(u' - ', entry[param])
            value = endtag_re.sub(u'', value)
        else:
            value = entry[param]

        return value

    except SiteParams.DoesNotExist:
        return ""

register.simple_tag(takes_context=True)(site_param)


def google_analitics():
    code = ""
    try:
        params = SiteParams.objects.language().get(site__id=settings.SITE_ID)
        code = u"%s" % (params.ga_code)
    except SiteParams.DoesNotExist:
        pass
    return mark_safe(code)
register.simple_tag(google_analitics)


def get_gravatar(email, size=40, rating='g', default=None):
    params = {'s': size, 'r': rating}
    if default:
        params['d'] = default
    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                   hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode(params)

    return gravatar_url
register.simple_tag(get_gravatar)
