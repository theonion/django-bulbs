# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('super_features', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basesuperfeature',
            name='query',
            field=json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', blank=True),
        ),
    ]
