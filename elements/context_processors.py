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
    debug = getattr(settings, 'DEBUG', False)
    if r:
        site = request.site
        site_id = 1
        site_name = getattr(settings, 'SITE_NAME', '')
        if site:
            try:
                site = Site.objects.get(domain=site.domain)
                site_id = site.id
                site_name = site.name
            except Site.DoesNotExist:
                pass
        setattr(settings, 'SITE_ID', site_id)

        (handler, args, kwargs) = r
        slug = kwargs['slug'] if 'slug' in kwargs else None
        if 'lang' in kwargs and kwargs['lang']:
            lang = kwargs['lang'].lower()
        if lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE

        return {'current_site': site, 'lang': lang, 'slug': slug,
                'debug': debug, 'site_name': site_name,
                'url_name': r.url_name,
                'admin_page': settings.THIS_IS_ADMIN}
    else:
        return {'lang': lang, 'debug': debug, 'site_name': site_name}
