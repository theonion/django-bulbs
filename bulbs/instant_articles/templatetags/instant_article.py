from django import template
from djbetty.templatetags.betty import AnonymousImageField


register = template.Library()


def image_url(image_id):
    image = AnonymousImageField(image_id)
    return image.get_crop_url(width=300, ratio="3x1")


def utm_url(absolute_uri, content):
    return "//" + absolute_uri + content.get_absolute_url() + "?utm_campaign=InstantArticles&utm_source=Facebook&utm_medium=SponsoredPromo"
