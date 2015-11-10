# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0005_auto_20151103_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcoverage',
            name='_image_alt',
            field=models.CharField(max_length=255, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='specialcoverage',
            name='_image_caption',
            field=models.CharField(max_length=255, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='specialcoverage',
            name='image',
            field=djbetty.fields.ImageField(default=None, alt_field=b'_image_alt', null=True, caption_field=b'_image_caption', blank=True),
        ),
    ]
