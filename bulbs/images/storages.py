import os
import json

from django.core.files.storage import Storage
from bulbs.images.conf import settings

import requests


class BettyCropperStorage(Storage):

    def delete(self, name):
        raise NotImplementedError

    def exists(self, name):
        src_url = "%s/%s/src" % (settings.BETTY_CROPPER['PUBLIC_URL'], name)
        r = requests.head(src_url)
        return r.status_code == 200

    def listdir(self, path):
        raise NotImplementedError

    def save(self, name, content):
        new_url = "%s/api/new" % settings.BETTY_CROPPER['ADMIN_URL']
        files = {
            'image': (os.path.basename(content.name), content)
        }
        r = requests.post(new_url, files=files)
        if r.status_code != 201:
            raise Exception("Couldn't save file to URL: \"%s\" (code %s, message: %s)" % (
                new_url, r.status_code, r.content))
        return json.dumps({'id': r.json()['id']})

    def size(self, name):
        raise NotImplementedError

    def url(self, name):
        return "%s/%s/original/600.jpg" % (settings.BETTY_CROPPER['PUBLIC_URL'], name)
