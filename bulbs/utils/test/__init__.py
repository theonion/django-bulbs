from mock import patch

import contextdecorator
import json
import logging
import os
import random
import string

from elasticsearch_dsl.connections import connections

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from djes.apps import indexable_registry
from djes.management.commands.sync_es import get_indexes, sync_index

from model_mommy import mommy
from rest_framework.test import APIClient
from six import PY3

from bulbs.content.models import Content


def make_content(*args, **kwargs):
    if "make_m2m" not in kwargs:
        kwargs["make_m2m"] = True

    if len(args) == 1:
        klass = args[0]
    else:
        models = indexable_registry.families[Content]
        model_keys = []
        for key in models.keys():
            if not key in ['content_content', 'poll_poll']:
                model_keys.append(key)
        key = random.choice(model_keys)
        klass = indexable_registry.all_models[key]

    content = mommy.make(klass, **kwargs)
    return content


def random_title():
    return ''.join([random.choice(string.ascii_uppercase) for _ in range(10)])


class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if not PY3 and isinstance(value, str):
            return unicode(value, errors='replace')  # TODO: Be stricter.
        if isinstance(value, set):
            return list(value)
        return super(JsonEncoder, self).default(value)


def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if hasattr(value, 'strftime'):
        if hasattr(value, 'hour'):
            return value.isoformat()
        else:
            return '%sT00:00:00' % value.isoformat()


class BaseIndexableTestCase(TestCase):
    """A TestCase which handles setup and teardown of elasticsearch indexes."""

    elasticsearchLogger = logging.getLogger('elasticsearch')

    def setUp(self):
        """ If you're reading this. I am gone and dead, presumably.
            Elasticsearch's logging is quite loud and lets us know
            about anticipated errors, so I set the level to ERROR only.
            If elasticsearch is giving you trouble in tests and you
            aren't seeing any info, get rid of this. God bless you.
        """
        self.elasticsearchLogger.setLevel(logging.ERROR)
        self.es = connections.get_connection("default")
        self.indexes = get_indexes()

        self.now = timezone.now()

        for index in list(self.indexes):
            self.es.indices.delete_alias("{}*".format(index), "_all", ignore=[404])
            self.es.indices.delete("{}*".format(index), ignore=[404])

        for index, body in self.indexes.items():
            sync_index(index, body)

    def tearDown(self):
        for index in list(self.indexes):
            self.es.indices.delete_alias("{}*".format(index), "_all", ignore=[404])
            self.es.indices.delete("{}*".format(index), ignore=[404])


class BaseAPITestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=admin)
        # reverse("content-detail")

    def give_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_content")
        change_perm = Permission.objects.get(codename="change_content")
        promote_perm = Permission.objects.get(codename="promote_content")
        self.admin.user_permissions.add(publish_perm, change_perm, promote_perm)

    def give_author_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_own_content")
        self.admin.user_permissions.add(publish_perm)

    def remove_permissions(self):
        self.admin.user_permissions.clear()


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
