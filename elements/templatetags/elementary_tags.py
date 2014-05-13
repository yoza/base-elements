"""
site params tags
"""
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
SUPPORTED = dict(settings.LANGUAGES)


@register.simple_tag(takes_context=True)
def logo_tag(context):
    """
    logo tag
    """
    logo = ""
    site_logo = getattr(settings, 'LOGO_IMAGE', ("../img/logo.png",
                                                 "0,0,85,85"))
    logo_text = getattr(settings, 'LOGO_TEXT', '')
    lang = ''
    if 'lang' in context and len(SUPPORTED) > 1:
        lang = context['lang']
        if lang is None or lang not in SUPPORTED:
            lang = settings.LANGUAGE_CODE
    try:
        params = SiteParams.objects.language().get(site__id=settings.SITE_ID)
        tags = 'span p br div sub sup a'
        tags = [re.escape(tag) for tag in tags.split()]
        tags_re = u'(%s)' % u'|'.join(tags)
        starttag_re = re.compile(r'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
        endtag_re = re.compile(u'</%s>' % tags_re)
        value = starttag_re.sub(u' - ', params.title)
        value = endtag_re.sub(u'', value)
        logo = u'<div class="logo_layer">\
                    <img usemap ="#logo_map" src="%s" alt="%s" id="img_logo"/>\
                    <map id ="logo_map" name="logo_map">\
                        <area href="/%s/" target="_self" id="area_logo_map" \
                              shape ="rect" coords ="%s" alt="%s"/>\
                    </map>\
                    <span class="logo-text">%s</span>\
                </div>' % (site_logo[0], value, lang, site_logo[1], value,
                           logo_text)
    except SiteParams.DoesNotExist:
        pass

    return mark_safe(logo)


@register.simple_tag
def site_param(param, tags=""):
    """
    site param tag
    """
    try:
        s_id = settings.SITE_ID
        entry = SiteParams.objects.language().values(param).get(site__id=s_id)
        if tags:
            tags = [re.escape(tag) for tag in tags.split()]
            tags_re = u'(%s)' % u'|'.join(tags)
            starttag_re = re.compile(r'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
            endtag_re = re.compile(u'</%s>' % tags_re)
            value = starttag_re.sub(u' - ', entry[param])
            value = endtag_re.sub(u' ', value)
        else:
            value = entry[param]

        return mark_safe(value)

    except SiteParams.DoesNotExist:
        return ""


@register.simple_tag
def google_analitics():
    """
    google analitics tag
    """
    code = ""
    try:
        params = SiteParams.objects.language().get(site__id=settings.SITE_ID)
        code = u"%s" % (params.ga_code)
    except SiteParams.DoesNotExist:
        pass
    return mark_safe(code)


@register.simple_tag
def get_gravatar(email, size=40, rating='g', default=None):
    """
    gravatar tag
    """
    params = {'s': size, 'r': rating}
    if default:
        params['d'] = default
    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + \
                   hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode(params)

    return gravatar_url


@register.simple_tag
def footer():
    """
    footer tag
    """
    try:
        params = SiteParams.objects.get(site__id=settings.SITE_ID)
        return params.footer

    except SiteParams.DoesNotExist:
        return ""


@register.simple_tag(takes_context=True)
def site_languages(context, sort=True, fullname=False):
    """
    site language tag
    """
    languages = ""
    if 'request' in context:
        request = context['request']
        lang = None
        if 'lang' in context:
            lang = context['lang']
        if lang is None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE
        path = request.META['PATH_INFO']
        clear_path = "/"
        if path != clear_path:
            items = path.strip('/').split('/')
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
        for i, language in enumerate(langs):
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
            languages += "<li %s ><span class='layer1'><span class='layer2'>"\
                         "<a %s href='%s'>%s</a></span></span></li>" % \
                         (css_class, css_class, path, lang_name)
        languages += "</ul>"

    return mark_safe(languages)


@register.simple_tag(takes_context=True)
def search_tag(context):
    """
    search tag
    """
    searches = ""
    if 'request' in context:
        request = context['request']
        lang = None
        if 'lang' in context:
            lang = context['lang']
        if lang is None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE

        if ('MSIE 6.0' in request.META.get('HTTP_USER_AGENT',
                                           '').upper() or
            'MSIE 7.0') in request.META.get('HTTP_USER_AGENT',
                                            '').upper():
            btn_img = getattr(settings,
                              'SEARCH_BTN_IMG_IE6',
                              '/static/elements/img/btn_search_ie6.gif')
        else:
            btn_img = getattr(settings,
                              'SEARCH_BTN_IMG',
                              '/static/elements/img/btn_search.png')
        placeholder = getattr(settings, 'SEARCH_PLACEHOLDER', "")
        plhol = ""
        if placeholder:
            plhol = 'placeholder="%s"' % unicode(_(placeholder))
        searches = u'<div id="search">'\
                   '<form method="get" action="/%s/search" id="searchform" '\
                   'autocomplete="off">'\
                   '<div class="line"><input type="search" name="query" '\
                   'id="query" %s /><input type="image" class="imgbtn" '\
                   'src="%s" alt="Search" />'\
                   '</div></form></div>' % (lang, plhol, btn_img)
        if getattr(settings, 'SEARCH_LABEL', None):
            searches += u'<script type="text/javascript">'\
                        'jQuery(document).ready(function(){clearInput('\
                        '"#searchform","#query", "%s")});</script>' \
                        % settings.SEARCH_LABEL
        elif ('MSIE' in request.META.get('HTTP_USER_AGENT',
                                       '').upper() and
              'MSIE 10.0' not in request.META.get('HTTP_USER_AGENT',
                                                 '').upper()):
            searches += u'<script type="text/javascript">'\
                        'jQuery(document).ready(function(){clearInput('\
                        '"#searchform","#query", "%s")});</script>' \
                        % placeholder
    return mark_safe(searches)


@register.simple_tag
def noscript_warning():
    """
    noscript warning
    """
    warning = u'<noscript>'
    warning += u'<div class="global-warning">'
    warning += u'<p class="site-message interface-text-dark">%s</p>' % \
               (unicode(_('Attention! JavaScript must be enabled in order '
                'for this page to function properly. However, '
                'it seems that you have JavaScript disabled or not '
                'supported by your browser.')))
    warning += u'<p class="site-message interface-text-dark">%s</p>' % \
        (unicode(_('Please enable JavaScript in your browser settings.')))
    warning += u'</div>'
    warning += u'</noscript>'

    return mark_safe(warning)


@register.simple_tag(takes_context=True)
def active_path(context):
    """
    active path
    """
    if 'request' in context:
        request = context['request']
        lang = ''
        if 'lang' in context and len(SUPPORTED) > 1:
            lang = context['lang'].lower()
            if not lang or lang not in SUPPORTED:
                lang = settings.LANGUAGE_CODE
        current_path = request.META['PATH_INFO']
        clear_path = "/"
        if current_path != clear_path:
            items = current_path.split('/')
            if str(items[1]) not in SUPPORTED:
                del items[1]
            for item in items:
                clear_path = os.path.join(clear_path, item)
        try:
            query_str = request.META['QUERY_STRING']
        except ValueError:
            query_str = None

        if clear_path.split('/')[1] == lang:
            current_path = '/' + lang + clear_path[3:]
        else:
            current_path = '/' + lang + clear_path
        if query_str:
            current_path += '?' + iri_to_uri(query_str)

    return mark_safe(current_path)


@register.simple_tag
def button_more(href="", alt="", label=_("In detail"), target="",
                aclass="btn_more", button_id=""):
    """
    This tag for use in IE7-IE8

    """
    btn_id = ""
    if button_id:
        btn_id = "id=%s" % button_id
    if label:
        label = unicode(_(label))
    code = u'<a href="%s" alt="%s" %s class="%s" %s>' % (href,
                                                         alt,
                                                         target,
                                                         aclass,
                                                         btn_id)
    code += u'<span class="btn_right"><span class="btn_left">'\
            '<span class="button_more">%s</span></span></span>' % label
    code += u'</a>'

    return mark_safe(code)
