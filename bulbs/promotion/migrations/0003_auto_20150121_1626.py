# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0002_content_list_to_pzone'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pzone',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='pzonehistory',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='pzoneoperation',
            options={'ordering': ['when', 'id']},
        ),
    ]
