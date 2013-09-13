from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from bulbs.images.fields import RemoteImageField

register = template.Library()

def crop_url(image, width, ratio="original", format="jpg"):
    return "%s/%s/%s/%s.%s" % (settings.BETTY_CROPPER['PUBLIC_URL'], image, ratio, width, format)

@register.simple_tag
def image_url(image, width, ratio='16x9', format='jpg'):
    if width is None:
        raise TemplateSyntaxError
    if isinstance(image, RemoteImageField):
        return image.crop_url(width=width, ratio=ratio, format=format)
    else:
        return crop_url(image, width=width, ratio=ratio, format=format)

@register.inclusion_tag('images/image.html', takes_context=True)
def image(context, image, width, ratio='16x9', format="jpg"):
    if width is None:
        raise TemplateSyntaxError
    context['image'] = image
    if isinstance(image, RemoteImageField):
        context['image_url'] = image.crop_url(width=width, ratio=ratio, format=format)
    else:
        context['image_url'] = crop_url(image, width=width, ratio=ratio, format=format)
    context['ratio'] = ratio
    context['width'] = width
    return context
