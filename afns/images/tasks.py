import os
import shutil
import logging
from urlparse import urlparse

from suds.client import Client

from celery.task import task
from django.conf import settings
    

@task
def clear_selection(selection_id):
    # We won't need this locally
    if settings.DEBUG:
        return
    
    logger = logging.getLogger()
    
    from afns.apps.images.models import ImageSelection
    selection = ImageSelection.objects.get(id=selection_id)
    crop_path = selection.image.crop_path(selection.ratio.slug, 10, absolute=True)
    directory = os.path.split(crop_path)[0]
    
    wsdl_url = "https://pantherportal.cdnetworks.com/wsdl/flush.wsdl"
    client = Client(wsdl_url)

    site_id = settings.CDN_STATIC_SITE_ID
    
    logger.info("Checking directory: %s" % directory)
    paths = []
    for file in os.listdir(directory):
        
        width = file.split(".")[0]
        crop_url = selection.image.crop_url(selection.ratio.slug, width)
        crop_pathinfo = urlparse(crop_url).path
        paths.append(crop_pathinfo)
        
        logger.info("Clearing file: %s, width: %s" % (file, width))
        
        os.remove(os.path.join(directory, file))
        
    client.service.flush(settings.CDN_USERNAME, settings.CDN_PASSWORD, 'paths', site_id, "\n".join(paths), False, False)
        
@task
def clear_crops(image_id):
    # We won't need this locally
    if settings.DEBUG:
        return
    
    logger = logging.getLogger()
    
    from afns.apps.images.models import Image
    image = Image.objects.get(id=image_id)
    directory = "%s%s/%s/" % (settings.IMAGE_CROP_ROOT, image.id/1000, image.id)
    
    wsdl_url = "https://pantherportal.cdnetworks.com/wsdl/flush.wsdl"
    client = Client(wsdl_url)
    
    site_id = settings.CDN_STATIC_SITE_ID
    
    logger.info("Checking directory: %s" % directory)
    if not os.path.exists(directory):
        return
    paths = []
    for crop_dir in os.listdir(directory):
        for file in os.listdir(os.path.join(directory, crop_dir)):        
            width = file.split(".")[0]
            crop_url = image.crop_url(crop_dir, width)
            crop_pathinfo = urlparse(crop_url).path
            paths.append(crop_pathinfo)
            os.remove(os.path.join(directory, crop_dir, file))
    
    logger.info("Clearing crops: %s" % paths)
    
    client.service.flush(settings.CDN_USERNAME, settings.CDN_PASSWORD, 'paths', site_id, "\n".join(paths), False, False)
    