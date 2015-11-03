# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('testcontent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcontentdetailimage',
            name='detail_image',
            field=djbetty.fields.ImageField(null=True, blank=True, caption_field='detail_caption', alt_field='detail_alt', default=None),
        ),
    ]
