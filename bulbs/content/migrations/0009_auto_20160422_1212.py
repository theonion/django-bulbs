# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_content_template_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuretype',
            name='instant_article',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='content',
            name='template_choice',
            field=models.IntegerField(default=0, choices=[(0, None), (1, b'special_coverage/landing.html')]),
        ),
    ]
