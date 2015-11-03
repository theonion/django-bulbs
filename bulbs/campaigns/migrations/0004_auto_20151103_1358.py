# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0003_auto_20150528_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignpixel',
            name='pixel_type',
            field=models.IntegerField(choices=[(0, 'Listing'), (1, 'Detail')], default=0),
        ),
    ]
