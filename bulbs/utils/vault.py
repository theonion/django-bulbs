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

CACHE_SEC = 60
BACKSTOP_CACHE_SEC = (60 * 60)


def read(path):
    """Primary interface to read data from Vault REST endpoint

    Uses 2 caches:
        short: Short-term caching to avoid overloading Vault service
        backstop: Longer-term cache, used as fallback if Vault request fails. Protects against vault service outages.
    """

    short_key = _make_key('short', path)
    backstop_key = _make_key('backstop', path)

    result = cache.get(short_key)

    if not result:

        try:
            result = _read_uncached(path)
            cache.set(short_key, result, CACHE_SEC=60)
            cache.set(backstop_key, result, BACKSTOP_CACHE_SEC=60)
        except VaultRequestError:
            log.exception('Vault read error: %s', path)
            # On endpoint failure, try to get value from longer-lasting cache
            result = cache.get(backstop_key)
            if not result:
                raise

    return result


def _make_key(*args):
    return ':'.join(['vault', 'read', CACHE_VERSION] + args])


def _read_uncached(path):
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
