import json

from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FileField, FieldFile
from django.core.exceptions import ValidationError

from rest_framework import serializers


from bulbs.images.conf import settings
from bulbs.images.storages import BettyCropperStorage


class RemoteImageSerializer(serializers.WritableField):

    def to_native(self, obj):
        if obj.name is None or obj.name == "":
            return None
        if obj.id is None:
            return None
        return {
            'id': obj.id,
            'caption': obj.caption,
            'alt': obj.alt
        }

    def from_native(self, data):
        if data:
            return json.dumps(data)
        return None


class RemoteImageFieldFile(FieldFile):
    def crop_url(self, width, ratio="original", format="jpg"):
        image_dir = ""
        for char in self.id:
            image_dir += char
            if len(image_dir) % 4 == 0:
                image_dir += "/"
        if image_dir.endswith("/"):
            image_dir = image_dir[:-1]
        return "%s/%s/%s/%s.%s" % (
            settings.BETTY_CROPPER['PUBLIC_URL'], image_dir, ratio, width, format)

    @property
    def id(self):
        try:
            data = json.loads(self.name)
            if isinstance(data, dict):
                return data.get('id')
        except (ValueError, TypeError):
            pass
        return self.name

    @id.setter
    def id(self, value):
        try:
            data = json.loads(self.name)
            if not isinstance(data, dict):
                data = {}
        except (ValueError, TypeError):
            data = {}
        data['id'] = value
        self.name = json.dumps(data)

    @property
    def caption(self):
        try:
            data = json.loads(self.name)
            if isinstance(data, dict):
                return data.get('caption')
        except (ValueError, TypeError):
            pass
        return None

    @caption.setter
    def caption(self, value):
        try:
            data = json.loads(self.name)
            if not isinstance(data, dict):
                data = {'id': self.name}
        except (ValueError, TypeError):
            data = {'id': self.name}
        data['caption'] = value
        self.name = json.dumps(data)

    @property
    def alt(self):
        try:
            data = json.loads(self.name)
            if isinstance(data, dict):
                return data.get('alt')
        except (ValueError, TypeError):
            pass
        return None

    @alt.setter
    def alt(self, value):
        try:
            data = json.loads(self.name)
            if not isinstance(data, dict):
                data = {'id': self.name}
        except (ValueError, TypeError):
            data = {'id': self.name}
        data['alt'] = value
        self.name = json.dumps(data)


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
        super(RemoteImageField, self).__init__(
            verbose_name, name, upload_to=self.upload_to, storage=self.storage, **kwargs)

    def validate(self, value, model_instance):
        try:
            data = json.loads(value.name)
        except TypeError:
            raise ValidationError("Invalid JSON document")

        if data:
            if 'id' in data and not isinstance(data['id'], basestring):
                raise ValidationError("")

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(FileField, self).pre_save(model_instance, add)
        return file

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, 'name'):
            value = value.name
        return super(RemoteImageField, self).get_prep_lookup(lookup_type, value)
