# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0003_auto_20150904_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='override',
            name='rate',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
