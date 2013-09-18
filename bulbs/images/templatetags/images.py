from django import template
from django.template import TemplateSyntaxError
from django.template.loader import select_template
from bulbs.images.fields import RemoteImageFieldFile

register = template.Library()


@register.simple_tag
def cropped_url(image, ratio, width, format='jpg'):
    if width is None:
        raise TemplateSyntaxError
    if not isinstance(image, RemoteImageFieldFile):
        raise TemplateSyntaxError("You must use a RemoteImageField as the first argument to this tag.")
    return image.crop_url(width=width, ratio=ratio, format=format)


@register.simple_tag(takes_context=True)
def cropped(context, image, ratio, width, format="jpg", caption=None, alt=None):
    if width is None:
        raise TemplateSyntaxError
    context['image'] = image
    if not isinstance(image, RemoteImageFieldFile):
        raise TemplateSyntaxError("You must use a RemoteImageField as the first argument to this tag.")
    context['image_url'] = image.crop_url(width=width, ratio=ratio, format=format)
    context['ratio'] = ratio
    context['width'] = width
    template = select_template(["images/crop.html", "images/_crop.html"])
    return template.render(context)