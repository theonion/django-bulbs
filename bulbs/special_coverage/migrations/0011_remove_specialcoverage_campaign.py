# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0010_auto_20160407_1705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialcoverage',
            name='campaign',
        ),
    ]
