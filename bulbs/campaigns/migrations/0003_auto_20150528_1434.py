# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_auto_20150318_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignpixel',
            name='pixel_type',
            field=models.IntegerField(default=0, choices=[(0, b'Listing'), (1, b'Detail')]),
        ),
    ]
