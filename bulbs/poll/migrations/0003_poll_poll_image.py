# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0002_poll_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='poll_image',
            field=djbetty.fields.ImageField(default=None, null=True, blank=True),
        ),
    ]
