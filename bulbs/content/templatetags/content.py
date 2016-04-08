from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def content_tunic_campaign_url(campaign_id):
    return "{}{}/{}/public".format(
        settings.TUNIC_BACKEND_ROOT,
        settings.TUNIC_API_PATH,
        campaign_id
    )
