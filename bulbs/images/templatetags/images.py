from django import template
from django.conf import settings

from bulbs.images.models import ImageAspectRatio

register = template.Library()


@register.simple_tag
def image_url(image, ratio_slug='16x9', width=360):
    if image:
        return image.crop_url(ratio_slug, width)
    return ""


def _image_context(image, ratio_slug, width):
    context = {'image': image, 'size': (0, 0), 'image_url': None}
    if image:
        if ratio_slug == 'original':
            height = (image.height * width) / image.width
            context['size'] = (width, height)
        else:
            ratio = ImageAspectRatio.objects.get_for_slug(ratio_slug)
            context['size'] = ratio.get_size(width=width)

        if settings.DEBUG:
            context['image_url'] = 'http://placehold.it/%sx%s' % context['size']
        else:
            context['image_url'] = image.crop_url(ratio_slug, width)
    context['ratio_slug'] = ratio_slug
    return context


@register.inclusion_tag('images/image_feature.html', takes_context=True)
def image_feature(context, image, ratio_slug, width):
    return context.update(_image_context(image, ratio_slug, width))


@register.inclusion_tag('images/image.html', takes_context=True)
def image(context, image, ratio_slug, width):
    return context.update(_image_context(image, ratio_slug, width))
