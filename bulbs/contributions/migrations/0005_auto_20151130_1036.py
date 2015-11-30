# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_auto_20151103_1358'),
        ('contributions', '0004_auto_20151103_1358'),
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
    ]
