# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0003_auto_20150423_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='config',
            field=json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', blank=True),
        ),
    ]
