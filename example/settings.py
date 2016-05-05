import os

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))
VAULT_BASE_URL = 'http://192.168.220.222:8200/v1/'
VAULT_BASE_SECRET_PATH = 'secrets/example'
VAULT_ACCESS_TOKEN = 'beepborp'

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

BULBS_TEMPLATE_CHOICES = (
    (1, "special_coverage/landing.html"),
)

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
    # bulbs content types
    "bulbs.poll",
    # local apps
    "bulbs.ads",
    "bulbs.api",
    "bulbs.campaigns",
    "bulbs.feeds",
    "bulbs.redirects",
    "bulbs.cms_notifications",
    "bulbs.content",
    "bulbs.instant_articles",
    "bulbs.promotion",
    "bulbs.special_coverage",
    "bulbs.sections",
    "bulbs.videos",
    # local testing apps
    "example.testcontent",
    "example.example_api",
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

DIGEST_ENDPOINT = "popular"
DIGEST_HOSTNAME = "homie"
DIGEST_OFFSET = 10
DIGEST_SITE = "bulbs"

SECRET_KEY = "no-op"

ES_DISABLED = False

ES_CONNECTIONS = {
    "default": {
        "hosts": [os.environ.get('ELASTICSEARCH_HOST', 'localhost')],
        "timeout": 30,
    }
}

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

CONTRIBUTIONS = {
    "EMAIL": {
        "FROM": "",
        "REPLY_TO": "",
        "SUBJECT": "",
        "TO": ["admin@theonion.com"]
    }
}

SODAHEAD_BASE_URL = 'https://onion.sodahead.com'
SODAHEAD_TOKEN_VAULT_PATH = 'sodahead/token'

VIDEOHUB_BASE_URL = 'http://www.onionstudios.com'
