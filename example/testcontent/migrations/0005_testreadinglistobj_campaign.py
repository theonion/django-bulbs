# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0005_campaign_tunic_campaign_id'),
        ('testcontent', '0004_testreadinglistobj'),
    ]

    operations = [
        migrations.AddField(
            model_name='testreadinglistobj',
            name='campaign',
            field=models.ForeignKey(to='campaigns.Campaign', null=True),
        ),
    ]
