# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_auto_20160613_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='template_choice',
            field=models.IntegerField(default=0, choices=[(0, None), (1, 'special_coverage/landing.html')]),
        ),
    ]
