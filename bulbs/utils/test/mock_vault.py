from mock import patch

import contextdecorator

class mock_vault(contextdecorator.ContextDecorator):
    """Decorator + context manager for mocking Vault secrets in unit tests.

    Usage:
            def test_vault(self):
                with mock_vault({'some/secret': 'my value'}):
                    self.assertEqual('my value', vault.read('some/secret'))

        .. OR ..

            @mock_vault({'some/secret': 'my value'})
            def test_vault(self):
                self.assertEqual('my value', vault.read('some/secret'))
    """

    def __init__(self, secrets=None):
        super(mock_vault, self).__init__()
        self.secrets = secrets or {}

    def __enter__(self):

        def read(path):
            if path not in self.secrets:
                raise Exception('Did not find secret key "{}" in mock vault: {}'.format(
                    path, self.secrets))
            return self.secrets[path]

        self.patched = patch('bulbs.utils.vault.read', side_effect=read)
        return self.patched.start()

    def __exit__(self, *args):
        self.patched.stop()
        return False
