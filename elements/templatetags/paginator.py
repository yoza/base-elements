from django import template
from django.conf import settings
from elements.backends.range_pagination import rangePagenation

register = template.Library()


def paginator(context, content_pages = None, slug = None):
    """
    Return short paginator like 'prev 1 ... 4 5 6 ... 20 next'
    Important add to settings 'PAGES_PER_PAGER' integer constant

    """
    if content_pages:
        if 'request' in context:
            request = context['request']
            url_params = request.GET.copy()
            if 'page' in url_params:
                del(url_params['page'])
            get_params = url_params.urlencode()

        page_url = get_params
        if slug:
            for sl in slug.split(','):
                if page_url:
                    page_url += '&'
                page_url += "%s=%s" % (sl, request.GET.get(sl, 'all'))
        try:
            selected_page = int(request.GET.get('page', 1))
        except ValueError:
            selected_page = 1

        letter = request.GET.get('letter', None)

        pager_per = getattr(settings, 'PAGES_PER_PAGER', content_pages.paginator.per_page)

        first_range = range(1, pager_per + 1)

        last_page_number = content_pages.paginator.num_pages

        page_range = rangePagenation(selected_page, content_pages, pager_per).page_range

        pages = content_pages

    return locals()

paginator = register.inclusion_tag('blocks/paginator.html',
                                            takes_context=True)(paginator)
