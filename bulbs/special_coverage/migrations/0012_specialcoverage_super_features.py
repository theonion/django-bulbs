# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0011_remove_specialcoverage_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='super_features',
            field=json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object', blank=True),
        ),
    ]
