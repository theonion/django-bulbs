from django.apps import apps
from django.core.management.base import BaseCommand

from djes.models import Indexable


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        app = apps.get_app('contributions')
        if not app:
            return

        for model in apps.get_models(app):
            if issubclass(model, Indexable):
                for instance in model.objects.all():
                    try:
                        instance.index()
                    except:
                        import pdb; pdb.set_trace()
