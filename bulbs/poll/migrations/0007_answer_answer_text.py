# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0006_answer_sodahead_answer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answer_text',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
