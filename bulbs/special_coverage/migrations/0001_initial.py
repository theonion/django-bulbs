# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialCoverage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField(unique=True, max_length=255, blank=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('query', json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', blank=True)),
                ('videos', json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
