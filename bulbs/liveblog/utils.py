from django.conf import settings


def get_liveblog_model():
    return getattr(settings, "BULBS_LIVEBLOG_MODEL")


def get_liveblog_author_model():
    return getattr(settings, "BULBS_LIVEBLOG_AUTHOR_MODEL", settings.AUTH_USER_MODEL)


def get_liveblog_serializer():
    return getattr(settings, "BULBS_LIVEBLOG_SERIALIZER")
