from django.apps import AppConfig


class LiveBlogConfig(AppConfig):
    name = 'bulbs.liveblog'

    def ready(self):
        # Recommended way to import signals in Django 1.7+
        import bulbs.liveblog.signals  # NOQA
