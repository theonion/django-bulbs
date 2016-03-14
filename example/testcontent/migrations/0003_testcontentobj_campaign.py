# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0005_campaign_tunic_campaign_id'),
        ('testcontent', '0002_auto_20151103_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcontentobj',
            name='campaign',
            field=models.ForeignKey(to='campaigns.Campaign', null=True),
        ),
    ]
