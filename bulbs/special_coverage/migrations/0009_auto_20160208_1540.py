# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

# NOTE: Referring to the Special Coverage model directly in this migration stopped
#       newer migrations from being run. This is fine though, since save() only needed to be run once


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0008_auto_20160118_1337'),
    ]

    operations = [
    ]
