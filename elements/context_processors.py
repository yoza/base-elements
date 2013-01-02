from django.core import urlresolvers
from django.conf import settings
from django.contrib.sites.models import Site


def locator(request):
    r = None
    try:
        r = urlresolvers.resolve(request.path_info)
    except urlresolvers.Resolver404:
        pass

    setattr(settings, 'THIS_IS_ADMIN', False)
    try:
        if 'admin' in request.path_info:
            setattr(settings, 'THIS_IS_ADMIN', True)
    except ValueError:
        pass

    lang = settings.LANGUAGE_CODE
    style = 'screen'
    debug = getattr(settings, 'DEBUG', False)
    if r:
        site_id = getattr(settings, 'SITE_ID', 1)
        site_name = getattr(settings, 'SITE_NAME', '')
        site = request.site
        if site:
            try:
                site = Site.objects.filter(domain=site.domain)
                if site.count():
                    site_id = site[0].id
                    site_name = site[0].name
            except Site.DoesNotExist:
                pass
        setattr(settings, 'SITE_ID', site_id)

        (handler, args, kwargs) = r

        slug = kwargs['slug'] if 'slug' in kwargs else None

        if 'lang' in kwargs and kwargs['lang'] and \
                kwargs['lang'].lower() in dict(settings.LANGUAGES):
            lang = kwargs['lang'].lower()

        if request.COOKIES.has_key('style'):
            style = request.COOKIES['style']

        return {'current_site': site,
               'current_style': style,
                        'lang': lang,
                        'slug': slug,
                       'debug': debug,
                   'site_name': site_name,
                    'url_name': r.url_name,
                  'admin_page': settings.THIS_IS_ADMIN
               }
    else:
        return {
                        'lang': lang,
                       'debug': debug,
                   'site_name': site_name,
               'current_style': style
               }
