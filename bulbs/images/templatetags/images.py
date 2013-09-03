from django import template
from django.template import TemplateSyntaxError

register = template.Library()


@register.simple_tag
def image_url(image, width, ratio='16x9', format='jpg'):
    if width is None:
        raise TemplateSyntaxError
    return image.crop_url(width=width, ratio=ratio, format=format)

@register.inclusion_tag('images/image.html', takes_context=True)
def image(context, image, width, ratio='16x9', format="jpg"):
    if width is None:
        raise TemplateSyntaxError
    context['image'] = image
    context['image_url'] = image.crop_url(width=width, ratio=ratio, format=format)
    context['ratio'] = ratio
    context['width'] = width
    return context
