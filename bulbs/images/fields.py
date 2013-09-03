from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FileField, FieldFile
from bulbs.images.conf import settings

from bulbs.images.storages import BettyCropperStorage


class RemoteImageFieldFile(FieldFile):
    def crop_url(self, width, ratio="original", format="jpg"):
        return "%s/%s/%s/%d.%s" % (settings.BETTY_CROPPER['PUBLIC_URL'], self.name, ratio, width, format)

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
