try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests

from django.conf import settings


class RequestFailure(requests.exceptions.RequestException):
    """The request failed."""


class TunicClient(object):

    def get(self, path):
        headers = {
            'Authorization': 'Token {}'.format(settings.TUNIC_REQUEST_TOKEN),
        }
        if settings.TUNIC_STAFF_BACKEND_ROOT in path:
            url = path
        else:
            url = self.handle_protocol_relative_paths(path)
        resp = requests.get(url, headers=headers)
        if not resp.ok:
            raise RequestFailure(response=resp)
        return resp

    def handle_protocol_relative_paths(self, path):
        url_base = settings.TUNIC_STAFF_BACKEND_ROOT
        if url_base.startswith('//'):
            url_base = 'http:' + url_base
        return urljoin(
            url_base, settings.TUNIC_API_PATH.rstrip('/') + '/' + path.lstrip('/')
        )

    def get_campaigns(self, filter_active=False):
        campaigns = {}
        path = "/campaign/"
        if filter_active:
            path += "?active=True"
        while path:
            resp = self.get(path).json()
            campaigns.update({
                c["id"]: c for c in resp.get("results", {})
            })
            path = resp.get("next")
        return campaigns

    def get_active_campaigns(self):
        return self.get_campaigns(filter_active=True)
