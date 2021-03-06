import os

MODULE_ROOT = os.path.dirname(os.path.realpath(__file__))
VAULT_BASE_URL = 'http://192.168.220.222:8200/v1/'
VAULT_BASE_SECRET_PATH = 'secrets/example'
VAULT_ACCESS_TOKEN = 'beepborp'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bulbs_test',
        'USER': 'bulbs',
        'PASSWORD': 'testing',
        'HOST': os.environ.get("DJANGO_DB_HOST", "localhost"),
        'PORT': '5432',
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
    "bulbs.infographics",
    "bulbs.notifications",
    "bulbs.redirects",
    "bulbs.cms_notifications",
    "bulbs.content",
    "bulbs.instant_articles",
    "bulbs.liveblog",
    "bulbs.promotion",
    "bulbs.special_coverage",
    "bulbs.sections",
    "bulbs.super_features",
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
    "BYLINE_REPORT": True,
    "EMAIL": {
        "BYLINE_RECIPIENTS": ["admin@theonion.com"],
        "FROM": "",
        "REPLY_TO": "",
        "SUBJECT": "",
        "TO": ["admin@theonion.com"]
    }
}

DEFAULT_CONTRIBUTOR_ROLE = 'Draft Writer'

SODAHEAD_BASE_URL = 'https://onion.sodahead.com'
SODAHEAD_TOKEN_VAULT_PATH = 'sodahead/token'

VIDEO_MODEL = "testcontent.TestVideoContentObj"
VIDEOHUB_BASE_URL = 'http://www.onionstudios.com'

FACEBOOK_TOKEN_VAULT_PATH = 'facebook/onion_token'
FACEBOOK_POST_TO_IA = False
FACEBOOK_PAGE_ID = '123456'
FACEBOOK_API_BASE_URL = 'https://graph.facebook.com/v2.6'
FACEBOOK_API_DEVELOPMENT_MODE = True
FACEBOOK_API_PUBLISH_ARTICLE = False
WWW_URL = "www.theonion.com"


# LiveBlog
BULBS_LIVEBLOG_MODEL = 'testcontent.TestLiveBlog'
