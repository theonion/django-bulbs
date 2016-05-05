# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TargetingOverride',
            fields=[
                ('url', models.URLField(primary_key=True, serialize=False)),
                ('targeting', json_field.fields.JSONField(default='null', help_text='Enter a valid JSON object')),
            ],
        ),
    ]
