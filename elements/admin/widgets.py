import re
import os
import warnings

from os.path import join
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext as _
from django.forms import Textarea
from django.template.loader import render_to_string


class TinyMCE(Textarea):
    cleanup_res = {
        re.compile(r'(\p{Zs}*)class="MsoNormal"', re.I | re.L | re.U): '',
        re.compile(r'<p(\p{Zs}*)/>', re.I | re.L | re.U): '',
        re.compile(r'<p>(\p{Zs}|&nbsp;)*</p>', re.I | re.L | re.U): '',
        re.compile(r'<p>(\p{Zs}|&nbsp;)+', re.I | re.L | re.U): '<p>',
        re.compile(r'(\p{Zs}|&nbsp;){2,}', re.I | re.L | re.U): '',
    }

    class Media:
        js = [join(settings.STATIC_URL, path) for path in (
            settings.DEFAULT_URL_TINYMCE,
        )]

    def __init__(self, language=None, attrs=None, **kwargs):
        template = 'admin/elements/tinymce4.html'
        self.template = kwargs.get('template', template)
        self.language = settings.LANGUAGE_CODE
        self.lang_list = ""
        for lang, name in settings.LANGUAGES:
            if self.lang_list:
                self.lang_list += ',' + lang
            else:
                self.lang_list = lang

        self.attrs = {'class': 'tinymce'}
        self.content_css = join(settings.STATIC_URL,
                                'elements/css/editor_content.css')
        if attrs:
            self.attrs.update(attrs)
        super(TinyMCE, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(TinyMCE, self).render(name, value, attrs)
        context = {
            'name':             name,
            'language':         self.language,
            'STATIC_URL':       settings.STATIC_URL,
            'content_css':      self.content_css,
            'lang_list':        self.lang_list,
        }

        # template = 'admin/elements/tinymce4.html'
        if 'tiny_mce' in settings.DEFAULT_URL_TINYMCE:
            # for deprecated tinymce 3.* versions
            self.template = 'admin/elements/tinymce.html'
            warnings.warn('The tinyMCE 3.x is deprecated. '
                          'Please use the new modern tinyMCE 4.x version.',
                          category=DeprecationWarning)

        return rendered + mark_safe(render_to_string(self.template, context))

    def do_cleanup(self, content):
        for pattern, replacement in self.cleanup_res.items():
            content = pattern.sub(replacement, content)
        return content

    def value_from_datadict(self, data, files, name):
        content = data.get(name)
        return self.do_cleanup(content)


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url

            file_name = str(value)
            path = "/".join(image_url.split("/")[:-1])
            fil = image_url.split("/")[-1]
            imfile = "".join(fil.split(".")[:-1]) + "." + (fil.split(".")[-1])

            thumb_url = os.path.join(path,
                                     settings.IMAGE_THUMB_PREFIX + imfile)

            output.append('<a style="display:block;float:left;'
                          'margin-right:10px;" href="{}" target="_blank">'
                          '<img src="{}" alt="{}" /></a> '.format(image_url,
                                                                  thumb_url,
                                                                  file_name))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))

        return mark_safe(u''.join(output))


class AdminBannerWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            file_type = image_url.split(".")[-1]
            if file_type.lower() in ("swf"):
                instance = getattr(value, "instance", None)
                if instance.slot.height and instance.slot.width:
                    height = instance.slot.height
                    width = instance.slot.width
                else:
                    return mark_safe(
                        '<span style="color:red;">{}</span>'.format(
                            '_("To allow for insert banner on this place, '
                            'please insert true `width` and `height` on the '
                            'banner slot before!")'))

                output.append(
                    '<script type="text/javascript"> var flashvars={};'
                    'var params={allowScriptAccess: "sameDomain",'
                    'allowFullScreen: "false",quality:"high",'
                    'wmode:"transparent",movie: "{}"};'
                    'var attributes={id: "banner_flash", name: "banner"};'
                    'swfobject.embedSWF("{}", "banner_flash","{}", "{}",'
                    '10.0.0","/media/flash/expressInstall.swf", flashvars,'
                    'params, attributes);</script><span id="banner_flash">'
                    '</span>{}'.format(image_url, image_url, width, height,
                                       _('Change:')))
            else:
                output.append('<a href="{}" target="_blank" '
                              'style="display:block;float:left;'
                              'margin-right:10px;"><img src="{}" alt="{}"/>'
                              '</a>'.format(image_url, image_url, file_name))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))

        return mark_safe(u''.join(output))


class AdminForeignImageWidget(RelatedFieldWidgetWrapper):

    def render(self, name, value, attrs=None):
        try:
            rel_value = getattr(self.rel.to.objects.get(pk=value),
                                self.rel.to.objects.model.IMAGE_ALIAS, None)
        except:
            rel_value = None
        output = []
        if rel_value and getattr(rel_value, "url", None):
            image_url = rel_value.url
            file_name = str(rel_value)
            path = "/".join(image_url.split("/")[:-1])
            fil = image_url.split("/")[-1]
            imfile = "".join(fil.split(".")[:-1]) + "." + (fil.split(".")[-1])

            thumb_url = os.path.join(path,
                                     settings.IMAGE_THUMB_PREFIX + imfile)
            output.append('<a href="{}" target="_blank">'
                          '<img src="{}" alt="{}" />'
                          '</a> {} '.format(image_url, thumb_url, file_name,
                                            _('Change:')))

        output.append(super(AdminForeignImageWidget,
                            self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class AdminIconWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append('<a href="{}" target="_blank" style='
                          '"display:block;float:left;margin-right:10px;">'
                          '<img src="%s" alt="%s" />'
                          '</a>'.format(image_url, image_url, file_name))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))

        return mark_safe(u''.join(output))
