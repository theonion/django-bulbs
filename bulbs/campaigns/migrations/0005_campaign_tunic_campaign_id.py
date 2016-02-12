# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0004_auto_20151103_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='tunic_campaign_id',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
    ]
