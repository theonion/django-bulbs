from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FileField, FieldFile

from rest_framework import serializers


from bulbs.images.conf import settings
from bulbs.images.storages import BettyCropperStorage


class RemoteImageSerializer(serializers.WritableField):

    def to_native(self, obj):
        return {
            'id': obj.id,
            'caption': obj.caption
        }

    def from_native(self, data):
        name = ""
        if 'id' in data:
            name += data['id']
        if 'caption' in data:
            name += "|%s" % data['caption']
        return name


class RemoteImageFieldFile(FieldFile):
    def crop_url(self, width, ratio="original", format="jpg"):
        image_dir = ""
        for char in self.id:
            image_dir += char
            if len(image_dir) % 4 == 0:
                image_dir += "/"
        if image_dir.endswith("/"):
            image_dir = image_dir[:-1]
        return "%s/%s/%s/%s.%s" % (settings.BETTY_CROPPER['PUBLIC_URL'], image_dir, ratio, width, format)

    @property
    def id(self):
        if self.name and "|" in self.name:
            return self.name.split("|")[0]
        return self.name

    @id.setter
    def id(self, value):
        if self.name and "|" in self.name:
            self.name = "%s|%s" % (value, self.name[self.name.index("|") + 1:])
        else:
            self.name = value

    @property
    def caption(self):
        if self.name and "|" in self.name:
            return self.name.split("|")[1]
        return None

    @caption.setter
    def caption(self, value):
        if self.name:
            if "|" in self.name:
                self.name = "%s|%s" % (self.name[:self.name.index("|")], value)
            else:
                self.name = "%s|%s" % (self.name, value)
        else:
            self.name = "|%s" % value


class RemoteImageField(FileField):
    description = _("RemoteImage")
    attr_class = RemoteImageFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        for arg in ('primary_key', 'unique'):
            if arg in kwargs:
                raise TypeError("'%s' is not a valid argument for %s." % (arg, self.__class__))

        self.storage = BettyCropperStorage()
        self.upload_to = settings.BETTY_CROPPER['ADMIN_URL']

        kwargs['max_length'] = kwargs.get('max_length', 100)
        super(FileField, self).__init__(verbose_name, name, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, 'name'):
            value = value.name
        return super(FileField, self).get_prep_lookup(lookup_type, value)
