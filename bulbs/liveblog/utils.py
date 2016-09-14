from django.apps import apps
from django.conf import settings


def get_liveblog_author_model_name():
    return getattr(settings, "BULBS_LIVEBLOG_AUTHOR_MODEL", settings.AUTH_USER_MODEL)


def get_liveblog_author_model():
    return apps.get_model(get_liveblog_author_model_name())
