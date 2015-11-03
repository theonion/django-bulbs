# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0004_specialcoverage_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcoverage',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
