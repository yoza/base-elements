"""
hierahy admin
"""
import os
import json
from django.forms import BooleanField
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.utils.translation import ugettext as _

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import force_text
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django import VERSION as DjangoVersion
from django.template.response import SimpleTemplateResponse

from elements.forms import dynamicforms
from elements.settings import HIERARHY_STATIC_URL, CSS_PATH


if DjangoVersion[:2] >= (1, 5):
    DJANGO_VERSION = 15
else:
    DJANGO_VERSION = "%d%d" % (DjangoVersion[:2][0], DjangoVersion[:2][1])

csrf_protect_m = method_decorator(csrf_protect)


class IncorrectLookupParameters(Exception):
    """
    Exseption
    """
    pass


class NavigationForm(dynamicforms.Form):
    """
    nav form
    """

    status = BooleanField(required=False)


class MyChangeList(ChangeList):
    """
    change list
    """
    def get_queryset(self, request, root=True):
        """
        override get queryset
        """
        if root:
            self.params['parent'] = None
        else:
            self.params = {}
        qus = super(MyChangeList, self).get_queryset(request)
        return qus


class HierarhyModelAdmin(admin.ModelAdmin):
    """
    hierahy model admin
    """

    class Media:
        """
        model media
        """

        if settings.DEBUG:
            CSS_PATH = '%s/src' % CSS_PATH

        css = {
            'all': [os.path.join(HIERARHY_STATIC_URL, CSS_PATH, path)
                    for path in (
                        'navigation.css',
                        )]
        }

    def process_item(self, item, form):
        """
        process item
        """
        pass

    def save_changed(self, request, queryset):
        """
        save changes
        """
        def id(name):
            """
            ID
            """
            return int(name.split('-')[-1])

        def realign(items, data, parent=None, position=1):
            """
            realign
            """
            for dat in data:
                item = items[id(dat['id'])]
                item.invalidate()
                item.position = position
                item.parent = parent
                position += 1
                item.save()
                realign(items, dat['children'], item, position)

        try:
            path = request.META['HTTP_REFERER']
        except ValueError:
            path = '.'

        if request.method == 'POST':
            items = dict(
                [(item.id, item) for item in self.model.objects.all()])
            redata = request.POST.get('navigation')
            hierarchy_data = json.loads(redata)
            realign(items, hierarchy_data)
            for form in NavigationForm.get_forms(request):
                assert form.is_valid()
                try:
                    item = items[int(form.id)]
                    self.process_item(item, form)
                except KeyError:
                    pass  # Should we fail silently?

            [entry.save() for entry in items.values()]

            self.message_user(
                request, _('The navigation was updated successfully. '
                           'You may edit it again below.'))

            return HttpResponseRedirect(path)

    save_changed.short_description = "%s" % _("Save selected changes")
    ordering = ["position"]
    item_template = 'admin/nav_item.html'

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        changelist_view
        """
        # super(HierarhyModelAdmin, self).changelist_view(request)
        media = self.media

        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        list_display = list(self.list_display)
        self.list_editable = list(self.list_editable)
        self.list_filter = list(self.list_filter)

        # Remove action checkboxes if there aren't any actions available.
        if not actions:
            try:
                list_display.remove('action_checkbox')
            except ValueError:
                pass

        try:
            list_display_links = self.get_list_display_links(request,
                                                             list_display)
        except AttributeError:
            list_display_links = []

        if self.list_max_show_all:
            list_max_show_all = self.list_max_show_all
        else:
            list_max_show_all = []

        try:
            if int(DJANGO_VERSION) > 13:
                cli = MyChangeList(request, self.model, list_display,
                                   list_display_links, self.list_filter,
                                   self.date_hierarchy, self.search_fields,
                                   self.list_select_related,
                                   self.list_per_page, list_max_show_all,
                                   self.list_editable, self)
            else:
                cli = MyChangeList(request, self.model, list_display,
                                   self.list_display_links, self.list_filter,
                                   self.date_hierarchy, self.search_fields,
                                   self.list_select_related,
                                   self.list_per_page, self.list_editable,
                                   self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.

        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(
                    request,
                    queryset=cli.get_queryset(request, False))
                if response:
                    return response

            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                self.message_user(request, msg)

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = \
                    self.response_action(request,
                                         queryset=cli.get_query_set(request,
                                                                    False))
                if response:
                    return response

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cli.formset = None

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = \
                self.get_action_choices(request)
        else:
            action_form = None

        media.add_js((
            HIERARHY_STATIC_URL + "js/mootools.js",
            HIERARHY_STATIC_URL + "js/nested.min.js",
            HIERARHY_STATIC_URL + "js/navigation.min.js",
        ))

        context = {
            'module_name': force_text(opts.verbose_name_plural),
            'title': _('Edit') + ' ' + _(opts.verbose_name_plural),
            'is_popup': cli.is_popup,
            'error': None,
            'cl': cli,
            'item_template': self.item_template,
            'media': mark_safe(media),
            'opts': opts,
            'has_add_permission': self.has_add_permission(request),
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
            'django_version': DJANGO_VERSION,
        }
        context.update(extra_context or {})
        context_instance = \
            template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response('admin/navigation_list.html',
                                  context, context_instance)

    def __call__(self, request, url):
        """
        call
        """
        if url is None:
            return self.changelist_view(request)
        return super(HierarhyModelAdmin, self).__call__(request, url)

    def save_model(self, request, obj, form, change):
        """
        save model
        """
        target = request.GET.get('target', None)
        position = request.GET.get('position', None)

        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
            else:
                target.invalidate()
                obj.move_to(target, position)

        super(HierarhyModelAdmin, self).save_model(request, obj, form, change)
