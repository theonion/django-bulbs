# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0002_auto_20151001_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freelanceprofile',
            name='is_manager',
            field=models.BooleanField(default=False),
        ),
    ]
