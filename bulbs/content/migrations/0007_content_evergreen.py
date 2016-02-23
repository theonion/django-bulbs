# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_content_tunic_campaign_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='evergreen',
            field=models.BooleanField(default=False),
        ),
    ]
