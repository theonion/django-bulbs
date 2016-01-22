# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0006_auto_20160105_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='featuretyperate',
            options={'ordering': ('feature_type__name',)},
        ),
        migrations.AlterModelOptions(
            name='lineitem',
            options={'ordering': ('-payment_date',)},
        ),
    ]
