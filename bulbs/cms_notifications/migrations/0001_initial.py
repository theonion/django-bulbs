# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CmsNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=110)),
                ('body', models.TextField(blank=True)),
                ('post_date', models.DateTimeField()),
                ('notify_end_date', models.DateTimeField()),
            ],
            options={
                'ordering': ['-id'],
            },
            bases=(models.Model,),
        ),
    ]
