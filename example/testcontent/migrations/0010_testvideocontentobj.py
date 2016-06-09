# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_content_instant_article_id'),
        ('videos', '0001_initial'),
        ('testcontent', '0009_testcontentobjthree'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestVideoContentObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, parent_link=True, to='content.Content')),
                ('videohub_ref', models.ForeignKey(blank=True, to='videos.VideohubVideo', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
    ]
