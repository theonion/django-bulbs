# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super_features', '0003_auto_20160711_1442'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contentrelation',
            unique_together=set([('parent', 'ordering')]),
        ),
    ]
