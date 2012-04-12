import os
from django.db import models
from django.conf import settings
from django.utils.translation import get_language
from pages.models import Language
try:
    from PIL import Image
except ImportError:
    import Image



class ImageManager(models.Manager):

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


    def validate_image(self, value):
        filetype = "." + value.name.split(".")[-1]
        if not filetype or filetype.lower() not in settings.FILEBROWSER_EXTENSIONS['Image']:
           raise ValidationError(_(u'Uploaded \'%s\' file is not an image. You can uploade only valid image file!') % filetype)


    def make_thumbnail(self, obj):
        if obj.image:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
            file = obj.image.name.split("/")[-1]
            thumb_path = os.path.join(settings.MEDIA_ROOT, settings.ALBUMS_PATH, self.model.path, settings.IMAGE_THUMB_PREFIX + file)

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
            path = settings.MEDIA_ROOT + "/".join(old_obj.image.name.split("/")[:-1])
            file = old_obj.image.name.split("/")[-1]
            thumb_path = os.path.join(path, settings.IMAGE_THUMB_PREFIX + file)
            if os.path.isfile(thumb_path):
                try:
                    os.unlink(thumb_path)
                except OSError:
                    pass


    def delete_image_children(self, obj):
        old_obj = obj.objects.get(pk=self.pk)
        path = settings.MEDIA_ROOT + "/".join(old_obj.image.name.split("/")[:-1])
        file = old_obj.image.name.split("/")[-1]
        thumb_path = os.path.join(path, settings.IMAGE_THUMB_PREFIX + file)
        if os.path.isfile(thumb_path):
            try:
                os.unlink(thumb_path)
            except OSError:
                pass


    def image_size(self, obj, lang):
        if not lang:
            lang = get_language()[:2]
        lang_id = Language.objects.get(code=lang)
        try:
            item = self.get(model=obj,language=lang_id)
        except self.model.DoesNotExist:
            item = None
        if item and item.image:
            try:
                image = Image.open(os.path.join(settings.MEDIA_ROOT, item.image.name))
                return image.size
            except OSError:
                pass
        return (0,0)


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

    def image_url(self, obj, lang):
        """
        Return image path

        """
        if not lang:
            lang = get_language()[:2]
        lang_id = Language.objects.get(code=lang)
        try:
            item = self.get(model=obj,language=lang_id)
        except self.model.DoesNotExist:
            item = None
        if item and item.image:
            path = os.path.join(settings.MEDIA_ROOT, item.image.name)
            if os.path.isfile(path):
                return unicode(settings.MEDIA_URL + item.image.name)

        return None
