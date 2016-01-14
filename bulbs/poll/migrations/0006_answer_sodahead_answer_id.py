# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0005_poll_sodahead_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='sodahead_answer_id',
            field=models.CharField(default=b'', max_length=20, blank=True),
        ),
    ]
