import os
import shutil

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bulbs.images.models import ImageCrop

class Command(BaseCommand):
    help = 'Clears all the image crops'

    def handle(self, *args, **options):
        if settings.DEBUG:
            crops_path = settings.IMAGE_CROP_ROOT
            for directory in os.listdir(crops_path):
                shutil.rmtree(os.path.join(crops_path), directory)
        else:
            print("Yeah, not a great idea to delete all the crops in a non-debug environment.")