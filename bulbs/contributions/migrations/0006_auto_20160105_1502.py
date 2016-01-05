# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0005_auto_20151130_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='amount',
            field=models.FloatField(default=0),
        ),
    ]
