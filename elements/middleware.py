# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.conf import settings
from django.utils import translation
from django.utils.cache import patch_vary_headers


class LazySite(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_site'):
            host = request.get_host()
            matches = Site.objects.filter(domain__iexact=host)
            if matches.exists():
                request._cached_site = matches.first()
            else:
                request._cached_site = Site.objects.get(id=settings.SITE_ID)
        return request._cached_site


class CurrentSiteMiddleware(object):

    def process_request(self, request):
        request.__class__.site = LazySite()


class ActiveLangMiddleware(object):
    """Activate language middleware. Use it to activate language from path"""

    def process_request(self, request):
        request.lang = translation.get_language_from_request(request,
                                                             check_path=True)
        translation.activate(request.lang)

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
