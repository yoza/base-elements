# -*- coding: utf-8 -*-
from django.template import RequestContext

from django.conf import settings

from elements.utils import auto_render

from elements.forms import handle_form


def details(request, lang=None, slug=None, raise404=True,
            template_name=settings.DEFAULT_TEMPLATE):

    context = RequestContext(request)

    if request.method == 'POST' and 'formname'\
            in request.POST and request.POST['formname'] is not None:
        response = handle_form(request.POST['formname'], request,
                               context, request.POST['formname'])
        if response:
            return response
    if 'template_name' not in context:
        context['template_name'] = template_name

    return context['template_name'], context

details = auto_render(details)
