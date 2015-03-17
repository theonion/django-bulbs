from django.db import models

from djbetty import ImageField


class Campaign(models.Model):

    sponsor_name = models.CharField(max_length=255)
    sponsor_logo = models.ImageField(null=True, blank=True)
    sponsor_url = models.URLField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    campaign_label = models.CharField(max_length=255)
    impression_goal = models.IntegerField(null=True, blank=True)


class CampaignPixel(models.Model):

    LOGO = 0
    CHOICES = (
        (LOGO, 'Logo'),
    )

    campaign = models.ForeignKey(Campaign, related_name='pixels')
    url = models.URLField()
    campaign_type = models.IntegerField(choices=CHOICES, default=LOGO)
