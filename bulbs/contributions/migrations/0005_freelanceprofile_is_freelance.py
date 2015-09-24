# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0004_auto_20150923_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelanceprofile',
            name='is_freelance',
            field=models.BooleanField(default=True),
        ),
    ]
