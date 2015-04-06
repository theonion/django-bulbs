# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0003_auto_20150121_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pzone',
            name='data',
            field=json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object', blank=True),
            preserve_default=True,
        ),
    ]
