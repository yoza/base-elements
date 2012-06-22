# -*- coding: utf-8 -*-

from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.core import urlresolvers
from django.contrib.sites.models import Site
from django.conf import settings

from elements.utils import get_site_from_request


class LazySite(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_site'):
            request._cached_site = get_site_from_request(request)
            if len(request._cached_site.domain.split(".")[-1]) == 0:
                request._cached_site = Site.objects.get(id=settings.SITE_ID)

        return request._cached_site


class CurrentSiteMiddleware(object):

    def process_request(self, request):
        request.__class__.site = LazySite()
        return None


class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    def process_request(self, request):
        r = language = None

        try:
            r = urlresolvers.resolve(request.path_info)
        except urlresolvers.Resolver404:
            pass

        if r:
            (handler, args, kwargs) = r
            language = kwargs['lang'] if 'lang' in kwargs else None

        if hasattr(request, 'session') and request.META['PATH_INFO'] == '/':
            try:
                del request.session['django_language']
            except AttributeError:
                pass
            except KeyError:
                pass

        if not language:
            language = translation.get_language_from_request(request)
        try:
            translation.activate(str(language))
        except UnicodeEncodeError:
            translation.activate(settings.LANGUAGE_CODE)
            #raise Http404(_('Site language should by ascii'))

        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
