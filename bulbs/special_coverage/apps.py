import django.apps


class AppConfig(django.apps.AppConfig):
    # Full Python path to the application
    name = 'bulbs.special_coverage'
    # Unique label (to avoid conflicts with property apps)
    label = 'bulbs_special_coverage'
