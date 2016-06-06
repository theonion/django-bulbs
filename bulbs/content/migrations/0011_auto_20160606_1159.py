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
            name='template_choice',
            field=models.IntegerField(default=0, choices=[(0, None)]),
        ),
    ]
