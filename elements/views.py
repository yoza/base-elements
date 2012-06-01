# -*- coding: utf-8 -*-
from django.template import RequestContext

from django.conf import settings

from elements.utils import auto_render

from elements.forms import handle_form


def details(request, page_id=None, slug=None, raise404=True,
            template_name=settings.DEFAULT_TEMPLATE, lang=None):

    context = RequestContext(request)

    if request.method == 'POST' and 'formname'\
            in request.POST and request.POST['formname'] is not None:
        response = handle_form(request.POST['formname'], request,
                               context, request.POST['formname'])
        if response:
            return response

    return context['template_name'], context
details = auto_render(details)
