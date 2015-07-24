# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_add_groups'),
    ]

    if django.VERSION >= (1, 8, 0):
        dependencies.insert(0,
            ('contenttypes', '0002_remove_content_type_name'))

    operations = [
        migrations.CreateModel(
            name='TemplateType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='template_type',
            field=models.ForeignKey(blank=True, to='content.TemplateType', null=True),
        ),
    ]
