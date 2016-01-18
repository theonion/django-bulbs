# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_content_instant_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='tunic_campaign_id',
            field=models.IntegerField(default=None, blank=True, null=True),
        ),
    ]
