# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0004_auto_20150403_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pzoneoperation',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_promotion.pzoneoperation_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
