try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def content_tunic_campaign_url(campaign_id):
    path = urljoin(
        settings.TUNIC_API_PATH,
        "campaign/{}/public".format(campaign_id)
    )
    return urljoin(settings.TUNIC_BACKEND_ROOT, path)
