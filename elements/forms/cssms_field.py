"""
Comma Separated String Multy Select Field

"""

from django.db import models
from django import forms
from django.core import exceptions
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.utils.datastructures import MergeDict, MultiValueDict
from django.utils.encoding import force_text


class DisabledSelect(forms.Select):

    def __init__(self, attrs=None, choices=(), disabled_choices=()):
        super(DisabledSelect, self).__init__(attrs, choices)
        self.disabled_choices = list(disabled_choices)

    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        disabled_html = ''
        if option_value in self.disabled_choices:
            disabled_html = mark_safe(' disabled="disabled"')
        else:
            disabled_html = ''
        return format_html('<option value="{}"{}{}>{}</option>',
                           option_value,
                           selected_html,
                           disabled_html,
                           force_text(option_label))


class CommaSepStrMultySelectWidget(DisabledSelect):
    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        elif not isinstance(value, list):
            value = value.split(',')
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html(
            '<select multiple="multiple"{}>', flatatt(final_attrs))]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)


class CommaSepStrMultySelectFormField(forms.MultipleChoiceField):
    widget = CommaSepStrMultySelectWidget

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(CommaSepStrMultySelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        return value

    def validate(self, value):
        """
        Validates that the input is a list or tuple.
        """
        if self.required and not value[0]:
            raise exceptions.ValidationError(self.error_messages['required'],
                                             code='required')
        # Validate that each value in the value list is in self.choices.
        for val in value:
            if not self.valid_value(val):
                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )


class CommaSepStrMultySelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def get_prep_value(self, value):
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, list):
            return ",".join(value)
        else:
            try:
                return isinstance(value, basestring)
            except NameError:
                return isinstance(value, str)

    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(CommaSepStrMultySelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname=name, choicedict=dict(
                self.choices): ",".join(
                    [choicedict.get(value, value)
                     for value in getattr(self, fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
