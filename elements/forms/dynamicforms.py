"""
dinamicforms
"""
import re

from django.template import Context, loader
from django import forms
from django.forms.forms import DeclarativeFieldsMetaclass
from django.utils.safestring import mark_safe
from django.utils import six


REPLACE_RES = \
    [re.compile('(<[^>]+) (%s=\\\\"[a-zA-Z0-9-_]+\.)#(\\\\")([^<]*>)' % s)
     for s in ('id', 'for', 'name')]


# This differs a bit from django.template.defaultfilters.addslashes,
# see http://code.djangoproject.com/ticket/2986
def addslashes(value):
    "Adds slashes - useful for passing strings to JavaScript, for example."
    value = value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

    # Line terminators according to ECMA-262
    value = value.replace('\n',
                          '\\n').replace('\r',
                                         '\\r').replace(u'\u2028',
                                                        '').replace(u'\u2029',
                                                                    '')

    return value


class FormCollection(list):
    """
    form collection
    """
    def are_valid(self):
        """
        validator
        """
        for form in self:
            if not form.is_valid():
                return False
        return True


class BaseForm(forms.BaseForm):
    """
    base form
    """
    #__metaclass__ = DeclarativeFieldsMetaclass

    def __init__(self, *args, **kwargs):

        self.postfix = kwargs.pop('postfix', '#')
        kwargs['prefix'] = kwargs.get('prefix',
                                      '') or getattr(self, 'PREFIX', '')
        self.template = kwargs.pop('template',
                                   '') or getattr(self, 'TEMPLATE', '')
        self.core = kwargs.pop('core', '') or getattr(self, 'CORE', [])
        self.id = kwargs.pop('id', '')
        super(BaseForm, self).__init__(*args, **kwargs)

    def add_prefix(self, field_name):
        prefixed = super(BaseForm, self).add_prefix(field_name)
        return self.postfix and ('%s.%s' % (prefixed,
                                            self.postfix)) or prefixed

    def header(self):
        """
        header
        """
        return u'<input type="hidden" name="%s" value="%s" />' % (
            self.add_prefix('id'), self.id)

    def render(self, how):
        """
        render
        """
        return u'%s%s' % (self.header(), getattr(self, how)())

    def render_js(self, how):
        """
        render js
        """
        data = addslashes(self.render(how))
        for replace_re in REPLACE_RES:
            data = re.sub(replace_re, '\\1 \\2\', FormId, \'\\3\\4', data)
        return mark_safe(u"['%s']" % data)

    def from_template(self, extra_context=None):
        """
        from template
        """
        if not extra_context:
            extra_context = {}
        template = loader.get_template(self.template)
        context = Context(dict([('form', self)]+extra_context.items()))
        return template.render(context)

    @classmethod
    def get_forms(cls, request, kwargs=None):
        """
        get dynamic forms
        """
        if not kwargs:
            kwargs = {}
        form = cls(request.POST, kwargs)
        id_name = form.add_prefix('id')

        form_ids = [key[len(id_name)-1:]
                    for key in request.POST.keys()
                    if key.startswith(id_name[:-1])]

        d_forms = FormCollection()

        for form_id in form_ids:

            new_kwargs = dict(kwargs.items()).update(
                {'postfix': form_id,
                 'id': request.POST[id_name[:-1] + form_id]})
            form = cls(request.POST, new_kwargs)
            if not form.id:
                # Ignore empty forms where no core field is specified
                core_available = False
                for core in form.core:
                    if request.POST.get(form.add_prefix(core), ''):
                        core_available = True
                        break
            if form.id or core_available:
                d_forms.append(form)

        return d_forms


class Form(six.with_metaclass(DeclarativeFieldsMetaclass, BaseForm)):
    """
    dynamic form
    """
    __metaclass__ = DeclarativeFieldsMetaclass
