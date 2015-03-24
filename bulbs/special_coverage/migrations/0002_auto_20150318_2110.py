# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0002_auto_20150318_1926'),
        ('special_coverage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='specialcoverage',
            name='campaign',
            field=models.ForeignKey(default=None, blank=True, to='campaigns.Campaign', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='specialcoverage',
            name='promoted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
