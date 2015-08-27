# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0002_auto_20150826_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='payment_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
