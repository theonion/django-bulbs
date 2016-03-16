# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answer_image',
            field=djbetty.fields.ImageField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='answer_type',
            field=models.TextField(default=b'text', blank=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='poll_image',
            field=djbetty.fields.ImageField(default=None, null=True, blank=True),
        ),
    ]
