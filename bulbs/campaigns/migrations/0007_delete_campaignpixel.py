# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0006_remove_campaignpixel_campaign'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CampaignPixel',
        ),
    ]
