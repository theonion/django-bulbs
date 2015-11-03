# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20150513_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='description',
            field=models.TextField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='content',
            name='slug',
            field=models.SlugField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='content',
            name='subhead',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='action_time',
            field=models.DateTimeField(verbose_name='action time', auto_now=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='change_message',
            field=models.TextField(verbose_name='change message', blank=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='object_id',
            field=models.TextField(verbose_name='object id', blank=True, null=True),
        ),
    ]
