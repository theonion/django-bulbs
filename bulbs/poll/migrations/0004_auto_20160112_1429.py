# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_content_instant_article'),
        ('poll', '0003_auto_20160112_1140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poll',
            name='id',
        ),
        migrations.AddField(
            model_name='poll',
            name='content_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=1, serialize=False, to='content.Content'),
            preserve_default=False,
        ),
    ]
