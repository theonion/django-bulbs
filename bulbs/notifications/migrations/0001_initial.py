# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('internal_title', models.CharField(max_length=512)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('headline', models.CharField(max_length=512)),
                ('is_published', models.BooleanField(default=False)),
                ('body', models.TextField(blank=True, null=True)),
                ('image', djbetty.fields.ImageField(blank=True, default=None, null=True)),
                ('clickthrough_url', models.URLField(blank=True, null=True)),
                ('clickthrough_cta', models.CharField(blank=True, max_length=30, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
