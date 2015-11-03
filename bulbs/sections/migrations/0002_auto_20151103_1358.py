# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='section',
            name='embed_code',
            field=models.TextField(blank=True, default=''),
        ),
    ]
