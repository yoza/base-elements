import os
import json
import django
from django.forms import BooleanField
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
from django.contrib import admin, messages
from django.utils.translation import ugettext as _
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe

from elements.backends import dynamicforms
from elements.settings import HIERARHY_STATIC_URL


csrf_protect_m = method_decorator(csrf_protect)


class NavigationForm(dynamicforms.Form):
    status = BooleanField(required=False)


class MyChangeList(ChangeList):
    def get_query_set(self, request):
        self.params['parent'] = None
        qs = super(MyChangeList, self).get_query_set(request)
        return qs


class HierarhyModelAdmin(admin.ModelAdmin):
    class Media:
        if settings.DEBUG:
            css_path = 'css/src'
        else:
            css_path = 'css'

        css = {
            'all': [os.path.join(HIERARHY_STATIC_URL, css_path, path)
                        for path in (
                            'navigation.css',
                        )
                   ]
        }

    def process_item(self, item, form):
        pass

    def save_changed(self, request, queryset):
        def id(name):
            return int(name.split('-')[-1])

        def realign(items, data, parent=None, position=1):
            for d in data:
                item = items[id(d['id'])]
                item.invalidate()
                item.position = position
                item.parent = parent
                position += 1
                item.save()
                realign(items, d['children'], item, position)

        try:
            path = request.META['HTTP_REFERER']
        except ValueError:
            path = '.'

        if request.method == 'POST':
            items = dict([(item.id, item)
                            for item in self.model.objects.all()])
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

            [item.save() for item in items.values()]
            self.message_user(request, _('The navigation was updated successfully. You may edit it again below.'))

            return HttpResponseRedirect(path)

    save_changed.short_description = _("Save selected changes")
    try:
        ordering = ["position"]
    except:
        ordering = []

    @csrf_protect_m
    @transaction.commit_on_success
    def changelist_view(self, request, extra_context=None):
        media = self.media
        model = self.model
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        list_display = list(self.list_display)
        list_editable = list(self.list_editable)
        list_filter = list(self.list_filter)

        # Remove action checkboxes if there aren't any actions available.
        if not actions:
            try:
                list_display.remove('action_checkbox')
            except ValueError:
                pass

        try:
            list_display_links = self.get_list_display_links(request, list_display)
        except AttributeError:
            list_display_links = []

        try:
            list_max_show_all = self.list_max_show_all
        except:
            list_max_show_all = []

        try:
            if int(django.VERSION[1]) > 3:
                cl = MyChangeList(request, self.model, list_display,
                    list_display_links, self.list_filter, self.date_hierarchy,
                    self.search_fields, self.list_select_related,
                    self.list_per_page, list_max_show_all, self.list_editable,
                    self)
            else:
                cl = MyChangeList(request, self.model, list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        except Exception, e:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html',
                                          {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk edit.
        # Try to look up an action first, but if this isn't an action the POST
        # will fall through to the bulk edit check, below.
        if actions and request.method == 'POST':
            response = self.response_action(request,
                                            queryset=cl.get_query_set(request))
            if response:
                return response

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        if cl.result_count == 1:
            module_name = force_unicode(opts.verbose_name)
        else:
            module_name = force_unicode(opts.verbose_name_plural)

        media.add_js((
            HIERARHY_STATIC_URL + "js/mootools.js",
            HIERARHY_STATIC_URL + "js/nested.js",
            HIERARHY_STATIC_URL + "js/navigation.js",
        ))

        context = {
            'module_name': module_name,
            'title': _('Edit') + ' ' + _(opts.verbose_name_plural),
            'is_popup': cl.is_popup,
            'error': None,
            'cl': cl,
            'item_template': self.item_template,
            'media': mark_safe(media),
            'opts': opts,
            'has_add_permission': self.has_add_permission(request),
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request,
                                           current_app=self.admin_site.name)
        return render_to_response('admin/navigation_list.html',
                                   context, context_instance)

    def __call__(self, request, url):
        if url is None:
            return self.changelist_view(request)
        return super(HierarhyModelAdmin, self).__call__(request, url)

    def save_model(self, request, obj, form, change):
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
