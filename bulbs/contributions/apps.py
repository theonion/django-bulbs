from django.apps import AppConfig


class ContributionsConfig(AppConfig):
    name = "bulbs.contributions"
    verbose_name = "Contributions"

    def ready(self):
        import bulbs.contributions.signals