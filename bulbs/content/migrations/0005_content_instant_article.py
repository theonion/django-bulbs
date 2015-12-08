# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_auto_20151103_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='instant_article',
            field=models.BooleanField(default=False),
        ),
    ]
