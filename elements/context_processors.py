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
    site_id = getattr(settings, 'SITE_ID', None)
    params = None
    rpi = None
    site = None
    try:
        rpi = urlresolvers.resolve(request.path_info)
    except urlresolvers.Resolver404:
        pass

    if rpi:
        if hasattr(request, 'site'):
            site = getattr(request, 'site', None)
        else:
            host = request.get_host()
            matches = Site.objects.filter(domain__iexact=host)
            if matches.exists():
                site = matches.first()
        if site:
            setattr(settings, 'SITE_ID', site.id)
        elif site_id:
            try:
                site = Site.objects.get(id=settings.SITE_ID)
            except Site.DoesNotExist:
                pass

        (handler, args, kwargs) = rpi

        slug = kwargs['slug'] if 'slug' in kwargs else None

        if ('lang' in kwargs and kwargs['lang'] and
                kwargs['lang'].lower() in dict(settings.LANGUAGES)):
            lang = kwargs['lang'].lower()
        try:
            params = SiteParams.objects.get(
                site__id=site.id)
        except SiteParams.DoesNotExist:
            pass

        if 'style' in request.COOKIES:
            style = request.COOKIES['style']

        return {'current_site': site,
                'current_style': style,
                'lang': lang,
                'slug': slug,
                'debug': debug,
                'site_name': site.name,
                'site_params': params,
                'url_name': rpi.url_name,
                'args': args,
                'handler': handler,
                'admin_page': settings.THIS_IS_ADMIN}
    else:
        return {'lang': lang,
                'debug': debug,
                'site_params': params,
                'site_name': site.name,
                'current_style': style}
