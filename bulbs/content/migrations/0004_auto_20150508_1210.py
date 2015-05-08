# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_template_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.content_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.tag_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
