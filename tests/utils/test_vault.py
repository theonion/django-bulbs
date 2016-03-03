from django.test import TestCase

from bulbs.utils.vault import read, VaultError, _make_key

from django.core.cache import cache

from mock import patch

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
