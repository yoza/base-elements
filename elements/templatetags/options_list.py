import datetime
try:
    from urllib import parse
except ImportError:
    import urllib as parse
from django.conf import settings
try:
    from django.contrib.admin.utils import (
        lookup_field, display_for_field, label_for_field)
except ImportError:
    from django.contrib.admin.util import (
        lookup_field, display_for_field, label_for_field)

from django.contrib.admin.views.main import (
    ALL_VAR, EMPTY_CHANGELIST_VALUE, ORDER_VAR, PAGE_VAR, SEARCH_VAR)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import formats
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text, force_text
from django.template import Library, Context, loader
from django.template.loader import get_template

register = Library()

DOT = '.'


def paginator_number(cl, i):
    if i == DOT:
        return u'... '
    elif i == cl.page_num:
        return mark_safe(u'<span class="this-page">%d</span> ' % (i+1))
    else:
        return mark_safe(u'<a href="%s"%s>%d</a> ' % (
            escape(cl.get_query_string({PAGE_VAR: i})),
            (i == cl.paginator.num_pages-1 and ' class="end"' or ''), i+1))
paginator_number = register.simple_tag(paginator_number)


def pagination(cl):
    paginator, page_num = cl.paginator, cl.page_num

    pagination_required = (
        not cl.show_all or not cl.can_show_all) and cl.multi_page
    if not pagination_required:
        page_range = []
    else:
        ON_EACH_SIDE = 3
        ON_ENDS = 2

        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if paginator.num_pages <= 10:
            page_range = range(paginator.num_pages)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(range(0, ON_EACH_SIDE - 1))
                page_range.append(DOT)
                page_range.extend(range(page_num - ON_EACH_SIDE, page_num + 1))
            else:
                page_range.extend(range(0, page_num + 1))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(
                    range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(
                    range(paginator.num_pages - ON_ENDS, paginator.num_pages))
            else:
                page_range.extend(range(page_num + 1, paginator.num_pages))

    need_show_all_link = cl.can_show_all and not cl.show_all and cl.multi_page
    return {
        'cl': cl,
        'pagination_required': pagination_required,
        'show_all_url': need_show_all_link and cl.get_query_string(
            {ALL_VAR: ''}),
        'page_range': page_range,
        'ALL_VAR': ALL_VAR,
        '1': 1,
    }
pagination = register.inclusion_tag('admin/pagination.html')(pagination)


def result_headers(cl):
    """
    Generates the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(field_name, cl.model,
                                     model_admin=cl.model_admin,
                                     return_attr=True)
        if attr:
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == 'action_checkbox':
                yield {
                    "text": text,
                    "class_attrib":
                    mark_safe(' class="action-checkbox-column"'),
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            if not admin_order_field:
                # Not sortable
                yield {
                    "text": text,
                    "sortable": False,
                }
                continue

        # OK, it is sortable if we got this far
        th_classes = ['sortable']
        order_type = ''
        new_order_type = 'asc'
        sort_priority = 0
        sorted = False
        # Is it currently being sorted on?
        if i in ordering_field_columns:
            sorted = True
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = ordering_field_columns.keys().index(i) + 1
            th_classes.append('sorted %sending' % order_type)
            new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []   # URL for removing this field from sort
        o_list_toggle = []   # URL for toggling order type for this field
        make_qs_param = lambda t, n: ('-' if t == 'desc' else '') + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "sortable": True,
            "sorted": sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_primary)}),
            "url_remove": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_remove)}),
            "url_toggle": cl.get_query_string(
                {ORDER_VAR: '.'.join(o_list_toggle)}),
            "class_attrib": mark_safe(
                th_classes and ' class="%s"' % ' '.join(th_classes) or '')
        }


def _boolean_icon(field_val):
    BOOLEAN_MAPPING = {True: 'yes', False: 'no', None: 'unknown'}
    return mark_safe(u'<img src="%simg/admin/icon-%s.gif" alt="%s" />' % (
        settings.ADMIN_MEDIA_PREFIX, BOOLEAN_MAPPING[field_val], field_val))


def items_for_result(cl, result, form, template, request):
    pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_class = ''
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except (AttributeError, ObjectDoesNotExist):
            result_repr = EMPTY_CHANGELIST_VALUE
        else:
            if f is None:
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = smart_text(value)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if not allow_tags:
                    result_repr = escape(result_repr)
                else:
                    result_repr = mark_safe(result_repr)
            else:
                if value is None:
                    result_repr = EMPTY_CHANGELIST_VALUE
                if isinstance(f.rel, models.ManyToOneRel):
                    result_repr = escape(getattr(result, f.name))
                else:
                    result_repr = display_for_field(value, f)
                if isinstance(f, models.DateField) \
                        or isinstance(f, models.TimeField):
                    row_class = ' class="nowrap"'
        if force_text(result_repr) == '':
            result_repr = mark_safe('&nbsp;')

        if field_name in cl.list_display_links:
            url = cl.url_for_result(result)
            # Convert the pk to something that can be used in Javascript.
            # Problem cases are long ints (23L) and non-ASCII strings.
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = pk
            value = result.serializable_value(attr)
            result_id = repr(force_text(value))[1:]
            yield render_template(result, template, request, cl)
        else:
            # By default the fields come from ModelAdmin.list_editable,
            # but if we pull the fields out of the form instead of
            # list_editable custom admins
            # can provide fields on a per request basis
            if form and field_name in form.fields:
                bf = form[field_name]
                result_repr = mark_safe(force_text(bf.errors) + force_text(bf))
            else:
                result_repr = conditional_escape(result_repr)
    if form:
        yield mark_safe(force_text(form[cl.model._meta.pk.name]))


def expanded(request, item):
    expand = False
    if "tree_expanded" in request.COOKIES:
        cookie_string = parse.unquote(request.COOKIES['tree_expanded'])
        if cookie_string:
            ids = [int(id)
                   for id in
                   parse.unquote(request.COOKIES['tree_expanded']).split(',')]
            if item.id in ids:
                expand = True
    return expand


def render_template(item, template, request, cl):
    try:
        children = item.get_children()
    except:
        children = None

    item.expanded = expanded(request, item)
    if item.expanded:
        ul_class = ""
    else:
        ul_class = "closed"
    content = template.render(Context(
        {'page': item, 'request': request, 'cl': cl}))
    node = '<li id="navigation-%s">%s%s</li>' % (
        item.id,
        content,
        children and '<ul class="' + ul_class + '">%s</ul>' % ''.join(
            [render_template(child, template, request, cl)
             for child in children]) or '')

    return mark_safe(node)


def results(cl, template, request):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield list(items_for_result(cl, res, form, template, request))
    else:
        for res in cl.result_list:
            yield list(items_for_result(cl, res, None, template, request))


def result_list(cl, item_template, request):
    template = loader.get_template(item_template)
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'results': list(results(cl, template, request))}
result_list = register.inclusion_tag("admin/navigation_line.html")(result_list)


def date_hierarchy(cl):
    if cl.date_hierarchy:
        field_name = cl.date_hierarchy
        year_field = '%s__year' % field_name
        month_field = '%s__month' % field_name
        day_field = '%s__day' % field_name
        field_generic = '%s__' % field_name
        year_lookup = cl.params.get(year_field)
        month_lookup = cl.params.get(month_field)
        day_lookup = cl.params.get(day_field)

        link = lambda d: cl.get_query_string(d, [field_generic])

        if year_lookup and month_lookup and day_lookup:
            day = datetime.date(int(year_lookup), int(month_lookup),
                                int(day_lookup))
            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup,
                                  month_field: month_lookup}),
                    'title': capfirst(
                        formats.date_format(day, 'YEAR_MONTH_FORMAT'))
                },
                'choices': [{'title': capfirst(
                    formats.date_format(day, 'MONTH_DAY_FORMAT'))}]
            }
        elif year_lookup and month_lookup:
            days = cl.query_set.filter(
                **{year_field: year_lookup,
                   month_field: month_lookup}).dates(field_name, 'day')
            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup}),
                    'title': year_lookup
                },
                'choices': [{
                    'link': link(
                        {year_field: year_lookup, month_field: month_lookup,
                         day_field: day.day}),
                    'title': capfirst(
                        formats.date_format(day, 'MONTH_DAY_FORMAT'))
                } for day in days]
            }
        elif year_lookup:
            months = cl.query_set.filter(
                **{year_field: year_lookup}).dates(field_name, 'month')
            return {
                'show': True,
                'back': {
                    'link': link({}),
                    'title': _('All dates')
                },
                'choices': [{
                    'link': link({year_field: year_lookup,
                                  month_field: month.month}),
                    'title': capfirst(
                        formats.date_format(month, 'YEAR_MONTH_FORMAT'))
                } for month in months]
            }
        else:
            years = cl.query_set.dates(field_name, 'year')
            return {
                'show': True,
                'choices': [{
                    'link': link({year_field: str(year.year)}),
                    'title': str(year.year),
                } for year in years]
            }
date_hierarchy =\
    register.inclusion_tag('admin/date_hierarchy.html')(date_hierarchy)


def search_form(cl):
    return {
        'cl': cl,
        'show_result_count': cl.result_count != cl.full_result_count,
        'search_var': SEARCH_VAR
    }
search_form = register.inclusion_tag('admin/search_form.html')(search_form)


@register.simple_tag
def admin_list_filter(cl, spec):
    tpl = get_template(spec.template)
    return tpl.render(Context({
        'title': spec.title,
        'choices': list(spec.choices(cl)),
        'spec': spec,
    }))


def admin_actions(context):
    """
    Track the number of times the action field has been rendered on the page,
    so we know which value to use.
    """
    context['action_index'] = context.get('action_index', -1) + 1
    return context
admin_actions = register.inclusion_tag("admin/actions.html",
                                       takes_context=True)(admin_actions)


def checkbox_active_actions(cl, page_id):
    """
    Return true if list has active actions
    """
    if cl.model_admin.actions_on_bottom or cl.model_admin.actions_on_top:

        return mark_safe('<input class="action-select" type="checkbox" name='
                         '"_selected_action" value="' + str(page_id) + '" />')

checkbox_active_actions = register.simple_tag(checkbox_active_actions)
