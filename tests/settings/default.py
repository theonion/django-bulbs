from os.path import join as pjoin, abspath, dirname, pardir


PROJ_ROOT = abspath(pjoin(dirname(__file__), pardir))
DATA_ROOT = pjoin(PROJ_ROOT, 'data')
ADMINS = (
    ('Webtech', 'webtech@theonion.com'),
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'bulbs.db'
    }
}
STATIC_ROOT = pjoin(PROJ_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = pjoin(PROJ_ROOT, 'media')
MEDIA_URL = '/media/'

ROOT_URLCONF = 'urls'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',

    # A test app to help with mixin stuff
    'testapp',

    'bulbs.base',
    'bulbs.images',
    'bulbs.markdown',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
)
SECRET_KEY = '9uab*ok!i=cnpkzcbuoa3y9d#&g589pq**4(n9t-jhsp-^yh7='
USE_TZ = True
ES_SERVER = {
    'url': 'localhost:9200',
    'path': 'testing',
    'timeout': 30,
    'connection_type': None
}
