import os
import re
import urllib
import hashlib
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import iri_to_uri
from django.utils.translation import ugettext_lazy as _

from elements.models import SiteParams


register = template.Library()
supported = dict(settings.LANGUAGES)


def logo_tag(context):
    logo = ""
    site_logo = getattr(settings, 'LOGO_IMAGE', ("maipage/img/logo.png",
                                                 "0,0,85,85"))
    lang = None
    if 'lang' in context:
        lang = context['lang']
    if lang == None or lang not in dict(settings.LANGUAGES):
        lang = settings.LANGUAGE_CODE

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
                        <area href="/%s" target="_self" id="area_logo_map" \
                              shape ="rect" coords ="%s" alt="%s"/>\
                    </map>\
                </div>' % (site_logo[0], value, lang, site_logo[1], value)

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

        return mark_safe(value)

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


def footer():

    try:
        params = SiteParams.objects.get(site__id=settings.SITE_ID)
        return params.footer

    except SiteParams.DoesNotExist:
        return ""

register.simple_tag(footer)


def site_languages(context, sort=True, fullname=False):

    languages = ""
    if 'request' in context:
        request = context['request']
        lang = None
        if 'lang' in context:
            lang = context['lang']
        if lang == None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE
        path = request.META['PATH_INFO']
        clear_path = "/"
        if path != clear_path:
            items = path.split('/')
            if str(items[1]) not in supported:
                del items[1]
            for item in items:
                clear_path = os.path.join(clear_path, item)
        try:
            query_str = request.META['QUERY_STRING']
        except ValueError:
            query_str = None

        langs = list(settings.LANGUAGES)

        if sort:
            langs = sorted(langs, key=lambda p: p[0])

        languages = "<ul>"
        for i,language in enumerate(langs):
            if clear_path.split('/')[1] == lang:
                path = '/' + language[0] + clear_path[3:]
            else:
                path = '/' + language[0] + clear_path

            if query_str:
                path += '?' + iri_to_uri(query_str)

            css_class = ""
            if i == 0:
                css_class = "class='first'"
            if str(language[0]) == lang:
                if css_class:
                    css_class = "class='active first'"
                else:
                    css_class = "class='active'"
            if len(langs) - i == 1:
                if css_class:
                    css_class = "class='active last'"
                else:
                    css_class = "class='last'"

            if fullname:
                lang_name = language[1]
            else:
                lang_name = language[1][:3]
            languages += "<li %s ><span class='layer1'><span class='layer2'><a %s href='%s'>%s</a></span></span></li>" % (css_class, css_class, path, lang_name)
        languages += "</ul>"

    return  mark_safe(languages)

register.simple_tag(takes_context=True)(site_languages)


@register.simple_tag
def search_tag(context):
    searches = ""
    if 'request' in context:
        request = context['request']
        lang = None
        if 'lang' in context:
            lang = context['lang']
        if lang == None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE

        csrf_token = request.META.get('CSRF_COOKIE', '')
        if 'MSIE 6.0' in request.META.get('HTTP_USER_AGENT', '').upper() or 'MSIE 7.0' in request.META.get('HTTP_USER_AGENT', '').upper():
            btn_img = getattr(settings,'SEARCH_BTN_IMG_IE6', '/static/elements/img/btn_search_ie6.png')
        else:
            btn_img = getattr(settings,'SEARCH_BTN_IMG', '/static/elements/img/btn_search.png')
        searches = u'<div id="search"><form method="get" action="/%s/search" id="searchform">\
                    <div style="display:none"><input type="hidden" name="csrfmiddlewaretoken" value="%s" /></div>\
                    <div class="line"><input type="text" name="query" id="query" />\
                    <input type="image" class="imgbtn" src="%s" alt="Search" />\
                    <input type="hidden" name="formname" value="search" /></div></form></div>' % (lang, csrf_token, btn_img)
        searches += u'<script type="text/javascript">jQuery(document).ready(function(){clearInput("#searchform","#query", "%s")});</script>' % (_("Search..."))

    return  mark_safe(searches)
register.simple_tag(takes_context=True)(search_tag)
