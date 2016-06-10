# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VideohubVideo',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=512)),
                ('description', models.TextField(blank=True, default='')),
                ('keywords', models.TextField(blank=True, default='')),
                ('image', djbetty.fields.ImageField(blank=True, null=True, alt_field='_image_alt', default=None, caption_field='_image_caption')),
                ('_image_alt', models.CharField(blank=True, null=True, max_length=255, editable=False)),
                ('_image_caption', models.CharField(blank=True, null=True, max_length=255, editable=False)),
                ('channel_id', models.IntegerField(blank=True, null=True, default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
