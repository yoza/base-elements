import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


try:
    from PIL import Image
except ImportError:
    import Image


class HierarchyManager(models.Manager):

    def hierarchy(self, parent=None):
        result = []

        if parent is None:
            nodes = self.root().order_by('position')
        else:
            nodes = self.filter(parent=parent).order_by('position')

        for node in nodes:
            result.append((node, self.hierarchy(parent=node)))

        return result

    def root(self, site=None):
        """
        Return a queryset with pages that don't have parents, a.k.a. root.
        """
        return self.filter(parent__isnull=True)


class ImageManager(HierarchyManager):

    def validate_image(self, value):
        filetype = "." + value.name.split(".")[-1]
        if not filetype or filetype.lower() not in \
                settings.FILEBROWSER_EXTENSIONS['Image']:
            e = _(u'Uploaded \'%s\' file is not an image. You can upload only valid image file!') % filetype
            raise ValidationError(e)

    def make_thumbnail(self, obj):
        if obj.image:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
            imfile = obj.image.name.split("/")[-1]
            thumb_path = os.path.join(settings.MEDIA_ROOT,
                                      settings.ALBUMS_PATH,
                                      self.model.path,
                                      settings.IMAGE_THUMB_PREFIX + imfile)

            msg = ""
            try:
                im = Image.open(file_path)
                im.thumbnail((settings.IMAGE_THUMB_SIZE), Image.ANTIALIAS)
                im.save(thumb_path)
            except IOError:
                msg = "%s: %s" % (file, _('Thumbnail creation failed.'))
            return msg

    def delete_thumbnail(self, obj):
        old_obj = self.get(pk=obj.pk)
        if old_obj.image:
            path = settings.MEDIA_ROOT + \
                    "/".join(old_obj.image.name.split("/")[:-1])
            imfile = old_obj.image.name.split("/")[-1]
            thumb_path = os.path.join(path,
                                      settings.IMAGE_THUMB_PREFIX + imfile)
            if os.path.isfile(thumb_path):
                try:
                    os.unlink(thumb_path)
                except OSError:
                    pass

    def delete_image_children(self, obj):
        old_obj = obj.objects.get(pk=self.pk)
        path = settings.MEDIA_ROOT + \
                "/".join(old_obj.image.name.split("/")[:-1])
        imfile = old_obj.image.name.split("/")[-1]
        thumb_path = os.path.join(path, settings.IMAGE_THUMB_PREFIX + imfile)
        if os.path.isfile(thumb_path):
            try:
                os.unlink(thumb_path)
            except OSError:
                pass

    def image_size(self, obj):
        try:
            item = self.get(model=obj)
        except self.model.DoesNotExist:
            item = None
        if item and item.image:
            try:
                image = Image.open(os.path.join(settings.MEDIA_ROOT,
                                                item.image.name))
                return image.size
            except OSError:
                pass
        return (0, 0)

    """
    def save(self, obj, force_insert=False, force_update=False):
        try:
            if self.pk:
                old_obj = obj.objects.get(pk=self.pk)
                if old_obj.image and old_obj.image.path != self.image.path:
                    try:
                        old_obj.image.delete()
                    except ValueError:
                        pass
                    obj.delete_thumbnail(self)
        except self.model.DoesNotExist:
            pass
        super(self.model, self).save(force_insert, force_update)
        obj.make_thumbnail(self)
    """

    def image_url(self, obj):
        """
        Return image path

        """
        try:
            item = self.get(model=obj)
        except self.model.DoesNotExist:
            item = None
        if item and item.image:
            path = os.path.join(settings.MEDIA_ROOT, item.image.name)
            if os.path.isfile(path):
                return unicode(settings.MEDIA_URL + item.image.name)

        return None
