# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def save_func(apps, schema_editor):
    # Trigger percolator save logic (new method ALWAYS saves percolator, previous
    # deleted percolator if not active).
    SpecialCoverage = apps.get_model("special_coverage", 'SpecialCoverage')
    for special in SpecialCoverage.objects.all():
        special.save()


class Migration(migrations.Migration):

    dependencies = [
        ('special_coverage', '0008_auto_20160118_1337'),
    ]

    operations = [
        migrations.RunPython(save_func, save_func)
    ]
