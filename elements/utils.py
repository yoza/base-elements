from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site, RequestSite, SITE_CACHE


def auto_render(func):
    """ Decorator that put automatically the template path in the context
        dictionary and call the render_to_response shortcut
    """
    def _dec(request, *args, **kwargs):
        t = None
        if kwargs.get('only_context', False):
            # return only context dictionary
            del(kwargs['only_context'])
            response = func(request, *args, **kwargs)
            if isinstance(response,
                          HttpResponse) or isinstance(response,
                                                      HttpResponseRedirect):
                raise Exception("cannot return context dictionary because \
                                a HttpResponseRedirect as been found")
            (template_name, context) = response
            return context
        if "template_name" in kwargs:
            t = kwargs['template_name']
            del kwargs['template_name']
        response = func(request, *args, **kwargs)
        if isinstance(response,
                      HttpResponse) or isinstance(response,
                                                  HttpResponseRedirect):
            return response
        (template_name, context) = response
        if not t:
            t = template_name
        context['template_name'] = t
        return render_to_response(t, context,
                                  context_instance=RequestContext(request))
    return _dec


def get_site_from_request(request, check_subdomain=True):
    """
    Returns the ``Site`` which matches the host name retreived from
    ``request``.

    If no match is found and ``check_subdomain`` is ``True``, the sites are
    searched again for sub-domain matches.

    If still no match, or if more than one ``Site`` matched the host name, a
    ``RequestSite`` object is returned.

    The returned ``Site`` or ``RequestSite`` object is cached for the host
    name retrieved from ``request``.
    """
    host = request.get_host().lower()
    if host in SITE_CACHE:
        # The host name was found in cache, return it. A cache value
        # of None means that a RequestSite should just be used.
        return SITE_CACHE[host] or RequestSite(request)
    matches = Site.objects.filter(domain__iexact=host)
    # We use len rather than count to save a second query if there was only
    # one matching Site
    count = len(matches)
    if not count and check_subdomain:
        matches = []
        for site in Site.objects.all():
            if host.endswith(site.domain.lower()):
                matches.append(site)
        count = len(matches)
    if count == 1:
        # Return the single matching Site
        site = matches[0]
    else:
        site = None
    # Cache the site (caching None means we should use RequestSite).
    SITE_CACHE[host] = site
    # Return site, falling back to just using a RequestSite.
    return site or RequestSite(request)
