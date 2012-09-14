from os.path import join
import re
from django import template
from django.conf import settings

from elements.models import  SiteParams


register = template.Library()


#@register.simple_tag
def header_tags(context):
    metadata = ''
    title = ''
    use_html5_plugins = getattr(settings, 'USE_HTML5_PLUGINS', False)
    if 'request' in context:
        request = context['request']
        if 'lang' in context:
            lang = context['lang']
        else:
            lang = None
        if lang == None or lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE
        current_page = None
        if 'current_page' in context:
            current_page = context['current_page']
            if current_page:
                title = current_page.title(lang)
        if not current_page or current_page.slug() in ('/','home'):
            try:
                tags = 'span p br div sub sup a'
                entry = SiteParams.objects.language(lang).get(site__id=settings.SITE_ID)
                tags = [re.escape(tag) for tag in tags.split()]
                tags_re = u'(%s)' % u'|'.join(tags)
                starttag_re = re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
                endtag_re = re.compile(u'</%s>' % tags_re)
                value = starttag_re.sub(u' - ', entry.title)
                title = endtag_re.sub(u'', value)
            except SiteParams.DoesNotExist:
                pass

        browser_request = request.META.get('HTTP_USER_AGENT', '').upper()

        metadata += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
        if 'MSIE 8.0' in browser_request:
            metadata += '<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />'
        metadata += '<title>%s</title>' % title

        #metadata += '<meta name="keywords" content="sabirov" />'
        metadata += '<meta http-equiv="cache-control" content="public" />'
        metadata += '<meta name="robots" content="follow, all" />'
        metadata += '<meta name="language" content="%s" />' % lang
        metadata += '<meta name="viewport" content="width=device-width; initial-scale=1.0;" />'

        css_path = join(settings.STATIC_URL, settings.STATIC_SUFFIX) + '/css/'

        js_path = join(settings.STATIC_URL, settings.STATIC_SUFFIX) + '/js/'

        metadata += '<link rel="stylesheet" type="text/css" href="%sscreen.css" charset="utf-8"/>' % css_path
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

        metadata += '<script type="text/javascript" src="%selements/js/jquery.min.js"></script>' % settings.STATIC_URL
        if use_html5_plugins:
            metadata += '<script src="%selements/js/jquery.details.min.js"></script>' % settings.STATIC_URL
        if 'MSIE' in browser_request:
            if 'MSIE 9.0' not in browser_request:
                    metadata += ' <script type="text/javascript" src="%selements/js/DD_roundies.js"></script>' %  settings.STATIC_URL
                    if use_html5_plugins:
                        metadata += ' <script type="text/javascript" src="%selements/js/html5shiv.js"></script>' %  settings.STATIC_URL
            if ('MSIE 6.0' in browser_request) or ('MSIE 7.0' in browser_request):
                metadata += '<script type="text/javascript" src="%selements/js/DD_belatedPNG-min.js"></script>'%  settings.STATIC_URL

        metadata += '<script type="text/javascript" src="%selements/js/elements.js" charset="utf-8"></script>' % settings.STATIC_URL
        metadata += '<script type="text/javascript" src="%sbase.js" charset="utf-8"></script>'% js_path
        metadata += '<link rel="shortcut icon" href="%sfavicon.ico" type="image/x-icon" />' % settings.STATIC_URL

    return metadata

register.simple_tag(takes_context=True)(header_tags)
