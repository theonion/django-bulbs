try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def content_tunic_campaign_url(campaign_id,
                               image_ratio=None,
                               image_width=None,
                               image_format=None):

    url_base = "campaign/{}/public".format(campaign_id)

    raw_params = {}
    if image_ratio:
        raw_params["image_ratio"] = image_ratio
    if image_width:
        raw_params["image_width"] = image_width
    if image_format:
        raw_params["image_format"] = image_format
    url_params = "{}".format(urlencode(raw_params))

    path = urljoin(
        settings.TUNIC_API_PATH,
        "{}?{}".format(url_base, url_params)
    )
    return urljoin(settings.TUNIC_BACKEND_ROOT, path)
