import os
import tempfile

from django.conf import settings


MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))


def pytest_configure():
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        MEDIA_ROOT=tempfile.mkdtemp("bettycropper"),
        TEMPLATE_DIRS=(os.path.join(MODULE_ROOT, 'tests', 'templates'),),
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rest_framework",
            "polymorphic",
            "elastimorphic",
            "bulbs.api",
            "bulbs.content",
            "bulbs.images",
            "tests.testcontent",),
        ROOT_URLCONF = 'tests.urls',
        
        ES_DISABLED = False,
        ES_URLS = ['http://localhost:9200'],
    )
