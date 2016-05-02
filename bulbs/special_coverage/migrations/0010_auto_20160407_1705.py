# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0009_auto_20160208_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialcoverage',
            name='image',
            field=djbetty.fields.ImageField(caption_field='_image_caption', default=None, null=True, alt_field='_image_alt', blank=True),
        ),
    ]
