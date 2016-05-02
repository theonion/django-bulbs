# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testcontent', '0007_testrecirccontentobject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testcontentobj',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='testreadinglistobj',
            name='campaign',
        ),
    ]
