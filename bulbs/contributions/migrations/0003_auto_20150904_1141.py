# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0002_auto_20150902_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contribution',
            name='content',
            field=models.ForeignKey(related_name='contributions', to='content.Content'),
        ),
    ]
