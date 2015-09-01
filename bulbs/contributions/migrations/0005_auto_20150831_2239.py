# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0004_auto_20150831_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribution',
            name='force_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contribution',
            name='payment_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
