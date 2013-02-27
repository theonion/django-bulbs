import os

from django.db import models

from bulbs.images.conf import settings

MAXIMUM_IMAGE_SIZE = (2000, 3000)


def image_locname(content_type, object_id, filename):
    pieces = [
        'images',
        content_type.app_label,
        content_type.model,
        str(int(object_id) / 1000),
        str(object_id),
        filename,
    ]
    return os.path.join(*pieces)


def image_upload_to(instance, filename):
    pieces = [
        'images',
        str(int(instance.id) / 1000),
        str(instance.id),
        "original",
        filename
    ]
    return os.path.join(*pieces)


class Image(models.Model):
    _width = models.IntegerField(blank=True, null=True, db_column='width')
    _height = models.IntegerField(blank=True, null=True, db_column='height')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    original = models.ImageField(max_length=255, upload_to=image_upload_to)
    caption = models.TextField(null=True, blank=True)
    alt = models.TextField(max_length=255, null=True, blank=True)
    credit = models.TextField(max_length=255, null=True, blank=True)

    def __repr__(self):
        cap = self.caption and (' %r' % self.caption) or ''
        return u'<Image %r%s>' % (
            self.location and os.path.basename(self.location.path) or 'None',
            cap)

    def get_width(self):
        """This method caches the width of the image on a field on the model"""
        if not self._width:
            try:
                width = self.location.width
                Image.objects.filter(pk=self.pk).update(_width=width)
                return width
            except:
                return 0
        else:
            return self._width

    def set_width(self, value):
        self._width = value
    width = property(get_width, set_width)

    def get_height(self):
        """This method caches the height of the image on a field on the model"""
        if not self._height:
            try:
                height = self.location.height
                Image.objects.filter(pk=self.pk).update(_height=height)
                return height
            except:
                return 0
        else:
            return self._height

    def set_height(self, value):
        self._height = value
    height = property(get_height, set_height)

    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)
        # cache width and height of this image by calling the proxy methods
        width, height = self.width, self.height

    def crop_path(self, ratio_slug, width, absolute=False):
        path = "%s/%s/%s/%s.jpg" % (self.id / 1000, self.id, ratio_slug, width)
        if absolute:
            return "%s%s" % (settings.IMAGE_CROP_ROOT, path)
        else:
            return path

    def crop_url(self, ratio_slug, width):
        return "%s%s" % (settings.IMAGE_CROP_URL, self.crop_path(ratio_slug, width))


class ImageAspectRatioManager(models.Manager):
    # This manager is heavily influenced by the ContentType manager in django core
    _cache = {}

    def get_for_slug(self, slug):
        try:
            it = self.__class__._cache[slug]
        except KeyError:
            it = self.get(slug=slug)
            self._add_to_cache(it)
        return it

    def get_for_id(self, id):
        try:
            it = self.__class__._cache[id]
        except KeyError:
            it = self.get(pk=id)
            self._add_to_cache(it)
        return it

    def clear_cache(self):
        self.__class__._cache.clear()

    def _add_to_cache(self, it):
        self.__class__._cache[it.slug] = it
        self.__class__._cache[it.id] = it


class ImageAspectRatio(models.Model):
    objects = ImageAspectRatioManager()

    slug = models.SlugField()
    width = models.IntegerField()
    height = models.IntegerField()

    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s (%sx%s)" % (self.slug, self.width, self.height)

    def get_size(self, width=None, height=None):
        if width is None and height is None:
            return (0, 0)
        if width:
            width = int(width)
            return (width, (self.height * width) / self.width)
        if height:
            height = int(height)
            return ((self.width * height) / self.height, height)
        return (0, 0)


class ImageSelectionManger(models.Manager):
    def get_or_create_for_image_and_ratio(self, image, ratio, commit=False):
        try:
            return self.model.objects.get(aspectratio=ratio, image=image)
        except ImageSelection.DoesNotExist:
            pass  # creating the new ImageSelection below
        try:
            center = self.model.objects.filter(image=image)[0].get_center()
        except IndexError:
            # this will calculate the width and height from the image on disk
            center = (image.width / 2, image.height / 2)

        selection = self.model(image=image, aspectratio=ratio)

        if ((image.width / ratio.width) * ratio.height) <= image.height:
            selection.width = image.width
            selection_height = (image.width / ratio.width) * ratio.height
            selection.origin_x = 0
            selection.origin_y = center[1] - (selection_height / 2)
        else:
            selection_height = image.height
            selection.width = (image.height / ratio.height) * ratio.width
            selection.origin_x = center[0] - (selection.width / 2)
            selection.origin_y = 0

        if selection.origin_x < 0:
            selection.origin_x = 0
        if selection.origin_y < 0:
            selection.origin_y = 0
        if selection.origin_y + selection_height > image.height:
            selection.origin_y = image.height - selection_height
        if selection.origin_x + selection.width > image.width:
            selection.origin_x = image.width - selection.width

        if commit:
            selection.save()

        return selection


class ImageSelection(models.Model):
    aspectratio = models.ForeignKey(ImageAspectRatio)
    image = models.ForeignKey(Image)
    origin_x = models.IntegerField()
    origin_y = models.IntegerField()
    width = models.IntegerField()

    objects = ImageSelectionManger()

    class Meta:
        unique_together = (("aspectratio", "image"),)

    # use a caching manager to store the ratio in python memory
    # since this will be called many many times per page
    def get_ratio(self):
        return ImageAspectRatio.objects.get_for_id(self.aspectratio_id)
    ratio = property(get_ratio, )

    def get_box(self):
        """This is the box that PIL's Image.crop uses."""
        height = (self.ratio.height * self.width) / self.ratio.width
        return (self.origin_x, self.origin_y, self.origin_x + self.width, self.origin_y + height)

    def get_center(self):
        height = (self.ratio.height * self.width) / self.ratio.width
        return (self.origin_x + (self.width / 2), self.origin_y + (height / 2))

    def __unicode__(self):
        return "%s cropping for %s" % (self.ratio.slug, self.image.location)
