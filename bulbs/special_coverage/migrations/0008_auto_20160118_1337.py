# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0007_auto_20160111_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='tunic_campaign_id',
            field=models.IntegerField(default=None, blank=True, null=True),
        ),
    ]
