import os

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
USE_TZ = True,

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

TEMPLATE_DIRS = (os.path.join(MODULE_ROOT, 'templates'),)

INSTALLED_APPS = (
    # django modules
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    # third parties
    "djbetty",
    "djes",
    "rest_framework",
    "rest_framework.authtoken",
    "polymorphic",
    # local apps
    "bulbs.api",
    "bulbs.campaigns",
    "bulbs.feeds",
    "bulbs.redirects",
    "bulbs.cms_notifications",
    "bulbs.content",
    "bulbs.promotion",
    "bulbs.special_coverage",
    "bulbs.sections",
    # local testing apps
    "example.testcontent",
    "bulbs.contributions",
)

ROOT_URLCONF = "example.urls"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'bulbs.promotion.middleware.PromotionMiddleware'
)

CELERY_ALWAYS_EAGER = True

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    )
}

SECRET_KEY = "no-op"

ES_DISABLED = False

ES_URLS = ['http://localhost:9200']
ES_INDEX = "django-bulbs"

ES_INDEX_SETTINGS = {
    "django-bulbs": {
        "index": {
            "analysis": {
                "filter": {
                    "autocomplete_filter": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 20
                    }
                },
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "autocomplete_filter"
                        ]
                    }
                }
            }
        }
    }
}
