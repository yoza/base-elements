"""
base context processor
"""

from django.core import urlresolvers
from django.conf import settings
from django.contrib.sites.models import Site
from .models import SiteParams


def locator(request):
    """
    context processor
    """

    setattr(settings, 'THIS_IS_ADMIN', False)
    try:
        if 'admin' in request.path_info:
            setattr(settings, 'THIS_IS_ADMIN', True)
    except ValueError:
        pass

    lang = settings.LANGUAGE_CODE
    style = 'screen'
    debug = getattr(settings, 'DEBUG', False)
    site_id = getattr(settings, 'SITE_ID', 1)
    site_name = getattr(settings, 'SITE_NAME', '')
    params = None
    rpi = None
    try:
        rpi = urlresolvers.resolve(request.path_info)
    except urlresolvers.Resolver404:
        pass

    if rpi:
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

        (handler, args, kwargs) = rpi

        slug = kwargs['slug'] if 'slug' in kwargs else None

        if 'lang' in kwargs and kwargs['lang'] and \
                kwargs['lang'].lower() in dict(settings.LANGUAGES):
            lang = kwargs['lang'].lower()
        try:
            params = SiteParams.objects.get(
                site__id=settings.SITE_ID)
        except SiteParams.DoesNotExist:
            pass

        if 'style' in request.COOKIES:
            style = request.COOKIES['style']

        return {'current_site': site,
                'current_style': style,
                'lang': lang,
                'slug': slug,
                'debug': debug,
                'site_name': site_name,
                'site_params': params,
                'url_name': rpi.url_name,
                'args': args,
                'handler': handler,
                'admin_page': settings.THIS_IS_ADMIN}
    else:
        return {'lang': lang,
                'debug': debug,
                'site_params': params,
                'site_name': site_name,
                'current_style': style}
