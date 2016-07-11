# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super_features', '0002_contentrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basesuperfeature',
            name='notes',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
