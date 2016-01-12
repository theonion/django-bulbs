# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0002_answer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poll',
            old_name='answer_text',
            new_name='question_text',
        ),
    ]
