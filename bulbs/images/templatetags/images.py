from django import template
from django.conf import settings
from django.template import TemplateSyntaxError

from bulbs.images.models import ImageAspectRatio, Image


register = template.Library()


@register.simple_tag
def image_url(image, width, ratio='16x9', quality=90, format='jpg'):
    if width is None or not isinstance(image, Image):
        raise TemplateSyntaxError
    return image.crop_url(ratio, width, format, quality)


def _image_context(image, ratio, width, format, quality):
    context = {'image': image, 'size': (0, 0), 'image_url': None}
    if image:
        if ratio == 'original':
            height = (image.height * width) / image.width
            context['size'] = (width, height)
        else:
            ratio_object = ImageAspectRatio.objects.get_for_slug(ratio)
            context['size'] = ratio_object.get_size(width=width)

        if settings.DEBUG:
            context['image_url'] = 'http://placehold.it/%sx%s' % context['size']
        else:
            context['image_url'] = image.crop_url(ratio, width, format, quality)
    context['ratio'] = ratio
    return context


@register.inclusion_tag('images/image.html', takes_context=True)
def image(context, image, width, ratio='16x9', quality=90, format="jpg"):
    if width is None or not isinstance(image, Image):
        raise TemplateSyntaxError
    return context.update(_image_context(image, ratio, width, format, quality))
