import os
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext as _


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

            output.append(u' <a style="display:block;float:left;\
                            margin-right:10px;" href="%s" target="_blank">\
                            <img src="%s" alt="%s" /></a> ' % \
                            (image_url, thumb_url, file_name))

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
                    return mark_safe(u'<span style="color:red;">%s</span>' % \
                _("To allow for insert banner on this place, please insert \
                  true 'width' and 'height' on the banner slot before!"))

                output.append(\
                u'<script type="text/javascript"> var flashvars = {}; \
                  var params = {allowScriptAccess: "sameDomain", \
                  allowFullScreen: "false",quality:"high",wmode:"transparent",\
                  movie: "%s"};\
                  var attributes = {id: "banner_flash", name: "banner"};\
                  swfobject.embedSWF("%s", "banner_flash","%s", "%s", \
                  "10.0.0","/media/flash/expressInstall.swf", flashvars, \
                  params, attributes);</script><span id="banner_flash"></span>\
                  %s' % (image_url, image_url, width, height, _('Change:')))
            else:
                output.append(u' <a href="%s" target="_blank" \
                                 style="display:block;float:left;\
                                 margin-right:10px;">\
                                 <img src="%s" alt="%s" /></a> ' % \
                                 (image_url, image_url, file_name))

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
            output.append(u' <a href="%s" target="_blank">\
                             <img src="%s" alt="%s" /></a> %s ' % \
                             (image_url, thumb_url, file_name, _('Change:')))

        output.append(super(AdminForeignImageWidget,
                            self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class AdminIconWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank" style=\
                             "display:block;float:left;margin-right:10px;">\
                             <img src="%s" alt="%s" /></a>' % \
                             (image_url, image_url, file_name))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))

        return mark_safe(u''.join(output))
