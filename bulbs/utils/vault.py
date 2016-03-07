# Hashicorp Vault client interface
#
# Should import module (instead of function) for easy vault test mocks:
#
#   import vault
#   vault.read(...)
#
import requests

from django.conf import settings

log = __import__('logging').getLogger(__name__)


def read(path):
    """Read a secret from Vault REST endpoint"""
    url = '{}/{}/{}'.format(settings.VAULT_BASE_URL.rstrip('/'),
                            settings.VAULT_BASE_SECRET_PATH.strip('/'),
                            path.lstrip('/'))

    headers = {'X-Vault-Token': settings.VAULT_ACCESS_TOKEN}
    resp = requests.get(url, headers=headers)
    if resp.ok:
        return resp.json()['data']
    else:
        log.error('Failed VAULT GET request: %s %s', resp.status_code, resp.text)
        raise Exception('Failed Vault GET request: {} {}'.format(resp.status_code, resp.text))
