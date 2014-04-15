import os

from django.conf import settings
from celery import Celery


MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))


def pytest_configure():

    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        USE_TZ=True,
        TEMPLATE_DIRS=(os.path.join(MODULE_ROOT, 'tests', 'templates'),),
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "rest_framework",
            "polymorphic",
            "elastimorphic",
            "bulbs.api",
            "bulbs.content",
            "bulbs.promotion",
            "tests.testcontent",),
        ROOT_URLCONF = 'tests.urls',
        TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.request"
        ),

        CELERY_ALWAYS_EAGER = True,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS = True,

        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework.authentication.SessionAuthentication',
            )
        },
        
        ES_DISABLED = False,
        ES_URLS = ['http://localhost:9200'],
    )

    app = Celery('proj')
    app.config_from_object(settings)
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
