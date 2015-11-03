# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0003_auto_20151103_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributorrole',
            name='payment_type',
            field=models.IntegerField(choices=[(0, 'Flat Rate'), (1, 'FeatureType'), (2, 'Hourly'), (3, 'Manual')], default=3),
        ),
        migrations.AlterField(
            model_name='rate',
            name='name',
            field=models.IntegerField(null=True, choices=[(0, 'Flat Rate'), (1, 'FeatureType'), (2, 'Hourly'), (3, 'Manual'), (4, 'Override')]),
        ),
    ]
