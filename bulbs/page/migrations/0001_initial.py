# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('notes', models.TextField()),
                ('status', models.IntegerField(default=0)),
                ('publish_date', models.DateTimeField(null=True, blank=True)),
                ('template_type', models.IntegerField(default=0)),
                ('tunic_campaign_id', models.IntegerField(default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
