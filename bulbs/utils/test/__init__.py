import json
import logging
import random
import string
import time

from elasticsearch_dsl.connections import connections

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from djes.apps import indexable_registry
from djes.management.commands.sync_es import get_indexes, sync_index

from model_mommy import mommy
from rest_framework.test import APIClient
import six

from bulbs.content.models import Content
from bulbs.super_features.utils import get_superfeature_model


SUPERFEATURE_MODEL = get_superfeature_model()


def make_content(*args, **kwargs):
    if "make_m2m" not in kwargs:
        kwargs["make_m2m"] = True

    if len(args) == 1:
        klass = args[0]
    else:
        models = indexable_registry.families[Content]
        model_keys = []
        for key in models.keys():
            if key not in [
                    'content_content',
                    'poll_poll',
                    'super_features_basesuperfeature',
                    'testcontent_testliveblog',
                    SUPERFEATURE_MODEL._meta.db_table]:
                model_keys.append(key)
        key = random.choice(model_keys)
        klass = indexable_registry.all_models[key]

    with transaction.atomic(savepoint=False):
        return mommy.make(klass, **kwargs)


def random_title():
    return ''.join([random.choice(string.ascii_uppercase) for _ in range(10)])


class JsonEncoder(json.JSONEncoder):

    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if six.PY2 and isinstance(value, str):
            return six.text_type(value, errors='replace')  # TODO: Be stricter.
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

    @classmethod
    def setUpClass(cls):
        super(BaseIndexableTestCase, cls).setUpClass()
        """ If you're reading this. I am gone and dead, presumably.
            Elasticsearch's logging is quite loud and lets us know
            about anticipated errors, so I set the level to ERROR only.
            If elasticsearch is giving you trouble in tests and you
            aren't seeing any info, get rid of this. God bless you.
        """
        logging.getLogger('elasticsearch').setLevel(logging.ERROR)
        # One-time setup per fixture
        cls.es = connections.get_connection("default")
        cls.indexes = get_indexes()

        cls._delete_es()

        for index, body in cls.indexes.items():
            sync_index(index, body)

    @classmethod
    def tearDownClass(cls):
        super(BaseIndexableTestCase, cls).tearDownClass()
        cls._delete_es()

    def setUp(self):
        super(BaseIndexableTestCase, self).setUp()

        self.now = timezone.now()

        # TODO: When to call me? setUp or setUpClass?
        self._wait_for_allocation()

    def tearDown(self):
        super(BaseIndexableTestCase, self).tearDown()

        # TODO: Move to setUp? Maybe don't do this the last (first in setUp) time?
        for index, body in self.indexes.items():
            self.es.indices.delete(index=index)
            self.es.indices.create(index=index, body=body)

    # TODO: Class method called by setUpClass?
    def _wait_for_allocation(self):
        """Wait for shards to be ready, to avoid flaky test errors when ES searches triggered before
        cluster is initialized.
        This is especially important for tests that do not trigger any sort of ES refresh.
        """

        # TODO: Or this?
        # self.es.cluster.health(wait_for_status='yellow', request_timeout=30)

        MAX_WAIT_SEC = 30
        start = time.time()
        while (time.time() - start) < MAX_WAIT_SEC:
            if all(len(shard) and shard[0]['state'] == 'STARTED'
                   for shard in self.es.search_shards()['shards']):
                return
        self.fail('One or more ES shards failed to startup within {} seconds'.format(MAX_WAIT_SEC))

    @classmethod
    def _delete_es(cls):
        cls.es.indices.delete_alias("_all", "_all", ignore=[404])
        cls.es.indices.delete("*", ignore=[404])


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
