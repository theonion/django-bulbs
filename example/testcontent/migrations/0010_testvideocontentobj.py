# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videohub_client', '0002_videohubvideo_channel_id'),
        ('content', '0010_auto_20160603_1217'),
        ('testcontent', '0009_testcontentobjthree'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestVideoContentObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, to='content.Content', primary_key=True)),
                ('videohub_ref', models.ForeignKey(null=True, blank=True, to='videohub_client.VideohubVideo')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
    ]
