# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_content_evergreen'),
        ('testcontent', '0006_anothertestreadinglistobj'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRecircContentObject',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('query', json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', blank=True)),
                ('foo', models.CharField(max_length=255)),
                ('bar', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
    ]
