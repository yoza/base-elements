"""
simple site header
"""
from os.path import join
import re
from django import template
from django.conf import settings

from elements.models import SiteParams


register = template.Library()


#@register.simple_tag
def header_tags(context):
    """
    header tag
    """
    metadata = ''
    title = ''
    use_html5_plugins = getattr(settings, 'USE_HTML5_PLUGINS', False)
    if 'request' in context:
        request = context['request']
        if 'lang' in context:
            lang = context['lang']
        else:
            lang = None
        if lang is None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE
        current_page = None
        if 'current_page' in context:
            current_page = context['current_page']
            if current_page:
                title = current_page.title(lang)
        if not current_page or current_page.slug() in ('/', 'home'):
            entry = []
            try:
                entry = SiteParams.objects.language(lang)
                entry = entry.get(site__id=settings.SITE_ID)
            except SiteParams.DoesNotExist:
                pass
            if entry:
                tags = 'span p br div sub sup a'
                tags = [re.escape(tag) for tag in tags.split()]
                tags_re = u'(%s)' % u'|'.join(tags)
                starttag_re = \
                    re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
                endtag_re = re.compile(u'</%s>' % tags_re)
                value = starttag_re.sub(u' - ', entry.title)
                title = endtag_re.sub(u'', value)

        browser_request = request.META.get('HTTP_USER_AGENT', '').upper()

        metadata += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
        if 'MSIE 8.0' in browser_request:
            metadata += '<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />'
        metadata += '<title>%s</title>' % title
        if entry:
            metadata += '<meta name="description" content="%s" />' % entry.mdescrip
            if 'extra_keywords' in context:
                keywords = "%s, %s" % (entry.mkeyword, context['extra_keywords'])
            else:
                keywords = entry.mkeyword
            metadata += '<meta name="keywords" content="%s" />' % keywords
        metadata += '<meta http-equiv="cache-control" content="public" />'
        metadata += '<meta name="robots" content="follow, all" />'
        metadata += '<meta name="language" content="%s" />' % lang
        metadata += '<meta name="viewport" content="width=device-width; initial-scale=1.0;" />'
        static_suffix = getattr(settings, 'STATIC_SUFFIX', '')
        css_path = join(settings.STATIC_URL, static_suffix) + '/css/'
        if settings.DEBUG:
            js_suf = 'js'
        else:
            js_suf = 'min.js'
        js_path = join(settings.STATIC_URL, static_suffix) + '/js/'

        metadata += '<link rel="stylesheet" type="text/css" href="%sscreen.css" title="screen" media="screen" charset="utf-8"/>' % css_path
        alternate_styles = getattr(settings, 'ALTERNATE_STYLES', ())
        if len(alternate_styles):
            for astyle in alternate_styles:
                metadata += '<link rel="alternate stylesheet" type="text/css" href="%s%s.css" title="%s" media="screen" charset="utf-8"/>' % (css_path, astyle, astyle)

        browser_label = None
        if 'MSIE' in browser_request:
            browser_label = 'ie'
            if 'MSIE 9.0' in browser_request:
                browser_label += "_9"

        elif 'KONQUEROR' in browser_request:
            browser_label = 'konqueror'
        elif 'WEBKIT' in browser_request:
            browser_label = 'webkit'
        elif 'OPERA' in browser_request:
            browser_label = 'opera'

        if browser_label:
            metadata += '<link rel="stylesheet" type="text/css" href="%s%s.css" charset="utf-8"/>' % (css_path, browser_label)

        if 'MSIE' in browser_request:
            metadata += '<link rel="stylesheet" type="text/css" href="%sfilters_ie.css" charset="utf-8"/>' % (css_path)
        if getattr(settings, 'USE_TINY_MCE', False):
            if settings.DEBUG:
                metadata += '<link rel="stylesheet" type="text/css" href="%seditor_content.css" charset="utf-8"/>' % (settings.STATIC_URL + 'elements/css/src/')
            else:
                metadata += '<link rel="stylesheet" type="text/css" href="%seditor_content.css" charset="utf-8"/>' % (settings.STATIC_URL + 'elements/css/')

        metadata += '<script type="text/javascript" src="%selements/js/jquery.min.js"></script>' % settings.STATIC_URL
        if use_html5_plugins:
            metadata += '<script src="%selements/js/jquery.details.min.js"></script>' % settings.STATIC_URL
        if 'MSIE' in browser_request:
            if 'MSIE 9.0' not in browser_request:
                    metadata += ' <script type="text/javascript" src="%selements/js/DD_roundies.js"></script>' %  settings.STATIC_URL
                    if use_html5_plugins:
                        metadata += ' <script type="text/javascript" src="%selements/js/html5shiv.js"></script>' % settings.STATIC_URL
            if ('MSIE 6.0' in browser_request) or ('MSIE 7.0' in browser_request):
                metadata += '<script type="text/javascript" src="%selements/js/DD_belatedPNG-min.js"></script>' %  settings.STATIC_URL

        metadata += '<script type="text/javascript" src="%selements/js/elements.%s" charset="utf-8"></script>' % (settings.STATIC_URL, js_suf)
        if alternate_styles:
            metadata += '<script type="text/javascript" src="%selements/js/stylesheetToggle.%s" charset="utf-8"></script>' % (settings.STATIC_URL, js_suf)

        metadata += '<script type="text/javascript" src="%sbase.%s" charset="utf-8"></script>' % (js_path, js_suf)

        metadata += '<link rel="shortcut icon" href="%s/favicon.ico" type="image/x-icon"/>' % settings.STATIC_URL

    return metadata

register.simple_tag(takes_context=True)(header_tags)
