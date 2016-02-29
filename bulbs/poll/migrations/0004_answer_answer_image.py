# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0003_poll_poll_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answer_image',
            field=djbetty.fields.ImageField(default=None, null=True, blank=True),
        ),
    ]
