# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
        ('testcontent', '0001_squashed_0011_testliveblog'),
    ]

    operations = [
        migrations.AddField(
            model_name='testliveblog',
            name='pinned_content',
            field=models.ForeignKey(to='content.Content', null=True, related_name='liveblog_pinned', blank=True),
        ),
    ]
