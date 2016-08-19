# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
        ('testcontent', '0010_testvideocontentobj'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestLiveBlog',
            fields=[
                ('content_ptr', models.OneToOneField(primary_key=True, to='content.Content', parent_link=True, serialize=False, auto_created=True)),
                ('recirc_content', models.ManyToManyField(related_name='liveblog_recirc', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
    ]
