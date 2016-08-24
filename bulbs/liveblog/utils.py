from django.conf import settings


def get_liveblog_author_model():
    return getattr(settings, "BULBS_LIVEBLOG_AUTHOR_MODEL", settings.AUTH_USER_MODEL)
