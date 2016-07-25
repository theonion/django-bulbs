# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='facebook_description',
            field=models.TextField(default=b'', max_length=1024, blank=True),
        ),
        migrations.AddField(
            model_name='content',
            name='facebook_image',
            field=djbetty.fields.ImageField(default=None, null=True, blank=True),
        ),
    ]
