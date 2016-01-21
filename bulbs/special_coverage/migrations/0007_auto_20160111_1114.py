# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0006_auto_20151109_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='specialcoverage',
            name='start_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
