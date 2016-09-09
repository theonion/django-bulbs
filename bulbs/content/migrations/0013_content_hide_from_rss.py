# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='hide_from_rss',
            field=models.BooleanField(default=False),
        ),
    ]
