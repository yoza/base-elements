from django.core import urlresolvers
from django.conf import settings
from django.contrib.sites.models import Site



def locator(request):
    r = None
    try:
        r = urlresolvers.resolve(request.path_info)
    except urlresolvers.Resolver404:
        pass

    settings.THIS_IS_ADMIN = False
    try:
        if 'admin' in request.path_info:
            settings.THIS_IS_ADMIN = True
    except ValueError:
        pass

    lang = settings.LANGUAGE_CODE
    if r:
        site = request.site
        site_id = 1
        if site:
            try:
                site = Site.objects.get(domain=site.domain)
                site_id = site.id
            except Site.DoesNotExist:
                pass
        setattr(settings, 'SITE_ID', site_id)

        (handler, args, kwargs) = r
        slug = kwargs['slug'] if 'slug' in kwargs else None
        if 'lang' in kwargs and kwargs['lang']:
            lang = kwargs['lang'].lower()
        if lang not in dict(settings.LANGUAGES):
            lang = settings.LANGUAGE_CODE

        return {'current_site': site, 'lang': lang, 'slug': slug, 'debug': settings.DEBUG,
                'admin_page': settings.THIS_IS_ADMIN, 'site_name': settings.SITE_NAME}
    else:
        return {'lang': lang, 'debug': settings.DEBUG}
