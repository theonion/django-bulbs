from django.conf import settings
from django.db import models

from djbetty import ImageField
from djes.models import Indexable

from bulbs.content.models import ElasticsearchImageField


class Notification(Indexable):
    """Model for site notifications."""

    # Internal
    internal_title = models.CharField(max_length=512)
    created_on = models.DateTimeField(auto_now_add=True)

    # Editorial
    headline = models.CharField(max_length=512, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    body = models.TextField(null=True, blank=True)
    image = ImageField(blank=True, null=True)
    clickthrough_url = models.URLField(blank=True, null=True)
    clickthrough_cta = models.CharField(blank=True, null=True, max_length=30)

    class Mapping:
        image = ElasticsearchImageField()

    def get_clickthrough_cta(self):
        """Return fallback cta, configured by the given property cms."""
        if not self.clickthrough_cta:
            return getattr(settings, "NOTIFICATION_CLICKTHROUGH_CTA", "Read More...")
        return self.clickthrough_cta
