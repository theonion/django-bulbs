import contextdecorator
import json
import logging
import random
import string
import time

from elasticsearch_dsl.connections import connections

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from djes.apps import indexable_registry
from djes.management.commands.sync_es import get_indexes, sync_index

from model_mommy import mommy
from rest_framework.test import APIClient
from six import PY2

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
            if key not in ['content_content', 'poll_poll']:
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
        if PY2 and isinstance(value, str):
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

        self._wait_for_allocation()

    def _wait_for_allocation(self):
        """Wait for shards to be ready, to avoid flaky test errors when ES searches triggered before
        cluster is initialized.
        This is especially important for tests that do not trigger any sort of ES refresh.
        """
        MAX_WAIT_SEC = 30
        start = time.time()
        while (time.time() - start) < MAX_WAIT_SEC:
            if all(len(shard) and shard[0]['state'] == 'STARTED'
                   for shard in self.es.search_shards()['shards']):
                return
        self.fail('One or more ES shards failed to startup within {} seconds'.format(MAX_WAIT_SEC))

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


