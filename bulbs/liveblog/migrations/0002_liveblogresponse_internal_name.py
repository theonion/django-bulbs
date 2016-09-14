# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveblog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='liveblogresponse',
            name='internal_name',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]
