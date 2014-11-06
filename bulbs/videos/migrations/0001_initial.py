# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('data', json_field.fields.JSONField(default='null', help_text=b'This is JSON that is returned from an encoding job', null=True, blank=True)),
                ('sources', json_field.fields.JSONField(default=[], help_text=b'This is a JSON array of sources.', null=True, blank=True)),
                ('poster_url', models.URLField(null=True, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Not started'), (1, b'Complete'), (2, b'In Progress'), (3, b'Failed')])),
                ('job_id', models.IntegerField(help_text=b'The zencoder job ID', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
