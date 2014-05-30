"""
app managers
"""
import os
import warnings

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
try:
    from PIL import Image
except ImportError:
    import Image


class HierarchyManager(models.Manager):
    """
    hierarhy manager
    """
    def hierarchy(self, parent=None):
        """
        hierarhy
        """
        result = []

        if parent is None:
            nodes = self.root().order_by('position')
        else:
            nodes = self.filter(parent=parent).order_by('position')

        for node in nodes:
            result.append((node, self.hierarchy(parent=node)))

        return result

    def root(self):
        """
        Return a queryset with pages that don't have parents, a.k.a. root.
        """
        return self.filter(parent__isnull=True)


class ImageManager(HierarchyManager):
    """
    image manager
    """
    def validate_image(self, value):
        """
        image validator
        """
        filetype = "." + value.name.split(".")[-1]
        if not filetype or filetype.lower() not in \
                settings.FILEBROWSER_EXTENSIONS['Image']:
            err = _(u'Uploaded \'%s\' file is not an image. '
                    'You can upload only valid image file!') % filetype
            raise ValidationError(err)

    def make_thumbnail(self, obj):
        """
        make custom thumbnail
        """
        if obj.image:
            imfile = obj.image.name.split("/")[-1]
            path = "/".join(obj.image.path.split("/")[:-1])
            msg = ''
            try:
                img = Image.open(obj.image.path)
                img.thumbnail((settings.IMAGE_THUMB_SIZE), Image.ANTIALIAS)
                img.save(os.path.join(path,
                                      settings.IMAGE_THUMB_PREFIX + imfile))
            except IOError:
                msg = "%s: %s" % (file, _('Thumbnail creation failed.'))
            return msg

    def delete_thumbnail(self, obj):
        """
        delete thumbnail
        """
        old_obj = self.get(pk=obj.pk)
        if old_obj.image:
            path = "/".join(old_obj.image.path.split("/")[:-1])
            imfile = old_obj.image.name.split("/")[-1]
            thumb_path = os.path.join(path,
                                      settings.IMAGE_THUMB_PREFIX + imfile)
            if os.path.isfile(thumb_path):
                try:
                    os.unlink(thumb_path)
                except OSError:
                    pass

    def delete_image_children(self, obj):
        """
        deprecated
        """
        obj = self.get(pk=obj.pk)
        warnings.warn('delete_image_children is deprecated. '
                      'Please use the new sections.py templatetags.',
                      category=DeprecationWarning)

    def image_size(self, obj):
        """
        retur image size
        """
        if obj and obj.image:
            try:
                image = Image.open(obj.image.path)
                return image.size
            except OSError:
                pass
        return (0, 0)

    def image_url(self, obj):
        """
        Return image path

        """
        if os.path.isfile(obj.image.path):
            return unicode(settings.MEDIA_URL + obj.image.name)

        return None
