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

        url_base = settings.TUNIC_STAFF_BACKEND_ROOT
        # Handle protocol-relative root paths
        if url_base.startswith('//'):
            url_base = 'http:' + url_base

        url = urljoin(url_base,
                      settings.TUNIC_API_PATH.rstrip('/') + '/' + path.lstrip('/'))

        resp = requests.get(url, headers=headers)
        if not resp.ok:
            raise RequestFailure(response=resp)
        return resp

    def get_active_campaigns(self):
        return {c['id']: c
                for c in self.get('/campaign/?active=true').json().get('results', {})}
