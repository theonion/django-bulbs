# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_content_evergreen'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='template_choice',
            field=models.IntegerField(choices=[(0, 'Default')], default=0),
        ),
    ]
