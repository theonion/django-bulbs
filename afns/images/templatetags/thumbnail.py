import urllib2
import os

from django import template
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, HttpResponseServerError

from afns.apps.images.models import Image, ImageSubject, ImageAspectRatio

register = template.Library()

def _get_image(image, subject):
    if image.__class__ == Image:
        return image
    
    if getattr(image, 'images', None).__class__.__name__ == 'GenericRelatedObjectManager':
        if subject:
            # If we have a subject, try to get one of those
            for sub in subject.split(","):
                images = image.images.filter(subject__name=sub)
                if images:
                    return images[0]
        else:
            # If no subject was specified, look for the default first
            default_images = image.images.filter(subject__name='default')
            if default_images:
                return default_images[0]
        
            # If there's no default, return the first image we find
            all_images = image.images.all()
            if all_images:
                return all_images[0]
        
    return None 

@register.simple_tag
def cropped_url(image, ratio_slug, width, subject=None):
    image = _get_image(image, subject)
    if image:
        return image.crop_url(ratio_slug, width)
    return ""

@register.inclusion_tag('images/cropped_feature.html', takes_context=True)
def cropped_feature(context, image, ratio_slug, width, subject="default"):
    image = _get_image(image, subject)
    context['image'] = image
    if image:    
        if ratio_slug == 'original':
            width = int(width)
            height = (image.height * width) / image.width
            context['size'] = (width, height)
        else:
            ratio = ImageAspectRatio.objects.get_for_slug(ratio_slug)
            context['size'] = ratio.get_size(width=width)
    else:
        context['size'] = (0,0)
    context['settings'] = settings
    context['ratio_slug'] = ratio_slug
    if image:
        context['image_url'] = image.crop_url(ratio_slug, width)
    else:
        context['image_url'] = None
    return context

@register.inclusion_tag('images/cropped.html', takes_context=True)
def cropped(context, image, ratio_slug, width, subject=None):
    image = _get_image(image, subject)   

    context['image'] = image
    if image:    
        if ratio_slug == 'original':
            width = int(width)
            height = (image.height * width) / image.width
            context['size'] = (width, height)
        else:
            ratio = ImageAspectRatio.objects.get_for_slug(ratio_slug)
            context['size'] = ratio.get_size(width=width)
    else:
        context['size'] = (0,0)
    context['settings'] = settings
    context['ratio_slug'] = ratio_slug
    if image:
        context['image_url'] = image.crop_url(ratio_slug, width)
    else:
        context['image_url'] = None
    return context
