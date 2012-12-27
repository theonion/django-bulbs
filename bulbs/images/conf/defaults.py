import os
from django.conf import settings

IMAGE_CROP_URL = '/images/crops/'
IMAGE_CROP_ROOT = os.path.join(settings.MEDIA_ROOT, 'images', 'crops')
