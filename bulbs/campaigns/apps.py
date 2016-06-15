import django.apps


class AppConfig(django.apps.AppConfig):
    # Full Python path to the application
    name = 'bulbs.campaigns'
    # Unique label (to avoid conflicts with property apps)
    label = 'bulbs_campaigns'
