# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0005_freelanceprofile_is_freelance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='override',
            options={'ordering': ('-updated_on',)},
        ),
    ]
