# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_auto_20160422_1212'),
        ('testcontent', '0008_auto_20160407_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestContentObjThree',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('body', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
    ]
