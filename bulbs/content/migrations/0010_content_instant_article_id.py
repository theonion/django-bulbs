# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_auto_20160422_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='instant_article_id',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
    ]
