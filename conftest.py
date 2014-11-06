import os

from django.conf import settings
from celery import Celery


MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))


def pytest_configure():
    """configurations used for pytest/pytest-django
    """

    # set up django settings
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
            # django modules
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            # third parties
            "djbetty",
            "elastimorphic",
            "rest_framework",
            "polymorphic",
            # local apps
            "bulbs.api",
            "bulbs.content",
            "bulbs.contributions",
            "bulbs.feeds",
            "bulbs.promotion",
            "bulbs.redirects",
            "bulbs.cms_notifications",
            # local testing apps
            "tests.testcontent",
        ),

        ROOT_URLCONF='tests.urls',

        TEMPLATE_CONTEXT_PROCESSORS=(
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.request"
        ),

        # django 1.7 drops some of the necessary middleware to make elastimorphic work
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),

        CELERY_ALWAYS_EAGER=True,

        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,

        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework.authentication.SessionAuthentication',
            )
        },
        
        ES_DISABLED=False,

        ES_URLS=['http://localhost:9200'],
    )

    # set up celery
    app = Celery('proj')
    app.config_from_object(settings)
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
