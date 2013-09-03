import os
from django.conf import settings

IMAGE_CROP_URL = '/images/crops/'
IMAGE_CROP_ROOT = os.path.join(settings.MEDIA_ROOT, 'images', 'crops')

BETTY_CROPPER = {
	'ADMIN_URL': 'http://localhost:9999',
	'PUBLIC_URL': 'http://localhost:8888'
}