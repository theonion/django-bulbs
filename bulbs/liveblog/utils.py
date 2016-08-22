from django.conf import settings

from bulbs.utils.methods import import_class


def get_liveblog_model():
    return import_class(getattr(settings, "BULBS_LIVEBLOG_MODEL"))


def get_liveblog_author_model():
    name = getattr(settings, "BULBS_LIVEBLOG_AUTHOR_MODEL", None)
    if name:
        return import_class(name)
    else:
        return settings.AUTH_USER_MODEL
