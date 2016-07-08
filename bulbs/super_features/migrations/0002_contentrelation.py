# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
        ('super_features', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordering', models.IntegerField()),
                ('child', models.ForeignKey(related_name='child', to='content.Content')),
                ('parent', models.ForeignKey(related_name='parent', to='content.Content')),
            ],
        ),
    ]
