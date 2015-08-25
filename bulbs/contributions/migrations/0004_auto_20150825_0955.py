# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0003_rolerateoverride'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributorrole',
            name='payment_type',
            field=models.IntegerField(default=3, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual')]),
        ),
        migrations.AlterField(
            model_name='rate',
            name='name',
            field=models.IntegerField(max_length=255, null=True, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual'), (4, b'Override')]),
        ),
    ]
