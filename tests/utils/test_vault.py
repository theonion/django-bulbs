from httmock import all_requests, HTTMock, response
from mock import patch
import requests

from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings

from bulbs.utils.vault import read, VaultError, _make_key, _read_endpoint


MEMORY_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'vault-test',
    }
}

TEST_DATA = 'RESPONSE'


class VaultReadTestCase(TestCase):

    def test_make_key(self):
        self.assertEqual('vault:read:1:one:two', _make_key('one', 'two'))

    def test_backstop_hit(self):
        with self.settings(CACHES=MEMORY_CACHE):
            cache.clear()

            # Saved to backstop cache
            with patch('bulbs.utils.vault._read_endpoint', return_value=TEST_DATA):
                self.assertEqual(TEST_DATA, read('path'))
                # Saved to caches
                self.assertEqual(TEST_DATA, cache.get('vault:read:1:short:path'))
                self.assertEqual(TEST_DATA, cache.get('vault:read:1:backstop:path'))

            # Loads from backstop cache
            with patch('bulbs.utils.vault._read_endpoint', side_effect=VaultError):
                self.assertEqual(TEST_DATA, read('path'))

    def test_backstop_miss(self):
        with patch('bulbs.utils.vault._read_endpoint', side_effect=VaultError):
            with patch('bulbs.utils.vault.logger') as mock_logger:
                with self.assertRaises(VaultError):
                    self.assertEqual(TEST_DATA, read('path'))
                self.assertTrue(mock_logger.exception.call_args)  # Exception logged

    def test_cache_miss_then_hit(self):
        with self.settings(CACHES=MEMORY_CACHE):
            cache.clear()

            with patch('bulbs.utils.vault._read_endpoint', return_value=TEST_DATA) as mock_endpoint:

                self.assertEqual(TEST_DATA, read('path'))
                self.assertEqual(1, mock_endpoint.call_count)

                # Saved to caches
                self.assertEqual(TEST_DATA, cache.get('vault:read:1:short:path'))
                self.assertEqual(TEST_DATA, cache.get('vault:read:1:backstop:path'))

                self.assertEqual(TEST_DATA, read('path'))
                self.assertEqual(1, mock_endpoint.call_count)


@override_settings(VAULT_BASE_URL='http://vault/v1',
                   VAULT_BASE_SECRIT_PATH='secret')
class VaultReadEndpointTestCase(TestCase):

    def test_success(self):
        @all_requests
        def api_mock(url, request):
            return response(200,
                            content={'data': {'key': 'value'}},
                            headers={'content-type': 'application/json'})

            with HTTMock(api_mock):
                self.assertEqual({'key': 'value'}, _read_endpoint('my/path'))

    def test_request_error(self):
        for status in [400, 404, 500]:
            @all_requests
            def api_mock(url, request):
                return response(status)

            with HTTMock(api_mock):
                with patch('bulbs.utils.vault.logger') as mock_logger:
                    with self.assertRaises(VaultError):
                        _read_endpoint('my/path')
                    self.assertTrue(mock_logger.error.call_args)  # Error logged

    def test_connection_error(self):
        with patch('bulbs.utils.vault.requests.get', side_effect=requests.ConnectionError):
            with patch('bulbs.utils.vault.logger') as mock_logger:
                with self.assertRaises(VaultError):
                    _read_endpoint('my/path')
                self.assertTrue(mock_logger.exception.call_args)  # Exception logged
