# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0002_auto_20150318_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcoverage',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='campaigns.Campaign', null=True),
            preserve_default=True,
        ),
    ]
