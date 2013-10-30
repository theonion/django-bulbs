from django import template
from django.conf import settings
from django.template import TemplateSyntaxError
from django.template.loader import select_template
from bulbs.images.fields import RemoteImageFieldFile

register = template.Library()


def crop_url(image_id, width, ratio="original", format="jpg"):
    image_dir = ""
    for char in image_id:
        image_dir += char
        if len(image_dir) % 4 == 0:
            image_dir += "/"
    if image_dir.endswith("/"):
        image_dir = image_dir[:-1]
    return "%s/%s/%s/%s.%s" % (settings.BETTY_CROPPER['PUBLIC_URL'], image_dir, ratio, width, format)


@register.simple_tag
def cropped_url(image, ratio, width, format='jpg'):
    if width is None:
        raise TemplateSyntaxError
    if isinstance(image, RemoteImageFieldFile):
        return crop_url(image.name, width=width, ratio=ratio, format=format)
    if isinstance(image, basestring):
        return crop_url(image, width=width, ratio=ratio, format=format)
    raise TemplateSyntaxError("You must use a RemoteImageField or string as the first argument to this tag.")


@register.simple_tag(takes_context=True)
def cropped(context, image, ratio, width, format="jpg", caption=None, alt=None):
    if width is None:
        raise TemplateSyntaxError
    context['image'] = image
    if isinstance(image, RemoteImageFieldFile):
        context['image_url'] = crop_url(image.name, width=width, ratio=ratio, format=format)
    elif isinstance(image, basestring):
        context['image_url'] = crop_url(image, width=width, ratio=ratio, format=format)
    else:
        raise TemplateSyntaxError("You must use a RemoteImageField as the first argument to this tag.")

    context['ratio'] = ratio
    context['width'] = width
    template = select_template(["images/crop.html", "images/_crop.html"])
    return template.render(context)