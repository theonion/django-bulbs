# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0007_auto_20160122_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineitem',
            name='contributor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='line_items'),
        ),
    ]
