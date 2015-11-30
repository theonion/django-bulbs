# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20150513_2326'),
        ('contributions', '0002_auto_20151001_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportContent',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('content.content',),
        ),
        migrations.AddField(
            model_name='freelanceprofile',
            name='payroll_name',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='freelanceprofile',
            name='is_manager',
            field=models.BooleanField(default=False),
        ),
    ]
