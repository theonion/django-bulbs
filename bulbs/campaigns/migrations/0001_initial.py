# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sponsor_name', models.CharField(max_length=255)),
                ('sponsor_logo', djbetty.fields.ImageField(default=None, null=True, blank=True)),
                ('sponsor_url', models.URLField(null=True, blank=True)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('campaign_label', models.CharField(max_length=255)),
                ('impression_goal', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CampaignPixel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('campaign_type', models.IntegerField(default=0, choices=[(0, b'Logo')])),
                ('campaign', models.ForeignKey(related_name='pixels', to='campaigns.Campaign')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
