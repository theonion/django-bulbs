# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0004_auto_20160112_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='sodahead_id',
            field=models.CharField(default=b'', max_length=20, blank=True),
        ),
    ]
