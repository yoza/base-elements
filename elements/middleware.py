# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.conf import settings


class LazySite(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_site'):
            request._cached_site = Site.objects.get_current(request)
            if len(request._cached_site.domain.split(".")[-1]) == 0:
                request._cached_site = Site.objects.get(id=settings.SITE_ID)

        return request._cached_site


class CurrentSiteMiddleware(object):

    def process_request(self, request):
        request.__class__.site = LazySite()
        return None
