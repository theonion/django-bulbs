# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VideoHubVideo',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(default=b'', blank=True)),
                ('poster_caption', models.CharField(max_length=255, null=True, blank=True)),
                ('poster_alt', models.CharField(max_length=255, null=True, blank=True)),
                ('poster', djbetty.fields.ImageField(default=None, alt_field=b'poster_alt', null=True, caption_field=b'poster_caption', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
