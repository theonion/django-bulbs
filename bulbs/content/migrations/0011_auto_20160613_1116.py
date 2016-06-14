# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_content_instant_article_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='instant_article_id',
            field=models.BigIntegerField(default=None, null=True, blank=True),
        ),
    ]
