# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0006_auto_20150925_1104'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='featuretyperate',
            unique_together=set([('role', 'feature_type')]),
        ),
    ]
