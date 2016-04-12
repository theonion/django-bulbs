# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0005_campaign_tunic_campaign_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignpixel',
            name='campaign',
        ),
    ]
