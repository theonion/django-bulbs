# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import bulbs.reading_list.mixins
import json_field.fields
import djbetty.fields


class Migration(migrations.Migration):

    replaces = [('testcontent', '0001_initial'), ('testcontent', '0002_auto_20151103_1402'), ('testcontent', '0003_testcontentobj_campaign'), ('testcontent', '0004_testreadinglistobj'), ('testcontent', '0005_testreadinglistobj_campaign'), ('testcontent', '0006_anothertestreadinglistobj'), ('testcontent', '0007_testrecirccontentobject'), ('testcontent', '0008_auto_20160407_1728'), ('testcontent', '0009_testcontentobjthree'), ('testcontent', '0010_testvideocontentobj'), ('testcontent', '0011_testliveblog')]

    dependencies = [
        ('campaigns', '0005_campaign_tunic_campaign_id'),
        ('content', '0002_add_groups'),
        ('content', '0012_auto_20160615_1605'),
        ('content', '0007_content_evergreen'),
        ('videos', '0001_initial'),
        ('content', '0009_auto_20160422_1212'),
        ('content', '0010_content_instant_article_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCategory',
            fields=[
                ('tag_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Tag', parent_link=True, serialize=False)),
                ('baz', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.tag',),
        ),
        migrations.CreateModel(
            name='TestContentObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='TestContentObjTwo',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('foo', models.CharField(max_length=255)),
                ('bar', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='TestContentDetailImage',
            fields=[
                ('testcontentobj_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='testcontent.TestContentObj', parent_link=True, serialize=False)),
                ('detail_caption', models.CharField(null=True, editable=False, blank=True, max_length=255)),
                ('detail_alt', models.CharField(null=True, editable=False, blank=True, max_length=255)),
                ('detail_image', djbetty.fields.ImageField(alt_field='detail_alt', null=True, caption_field='detail_caption', blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
            bases=('testcontent.testcontentobj',),
        ),
        migrations.CreateModel(
            name='TestReadingListObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', bulbs.reading_list.mixins.ReadingListMixin),
        ),
        migrations.CreateModel(
            name='AnotherTestReadingListObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('haa', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', bulbs.reading_list.mixins.ReadingListMixin),
        ),
        migrations.CreateModel(
            name='TestRecircContentObject',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('query', json_field.fields.JSONField(help_text='Enter a valid JSON object', blank=True, default={})),
                ('foo', models.CharField(max_length=255)),
                ('bar', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
        migrations.CreateModel(
            name='TestContentObjThree',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('body', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='TestVideoContentObj',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('videohub_ref', models.ForeignKey(to='videos.VideohubVideo', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
        migrations.CreateModel(
            name='TestLiveBlog',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='content.Content', parent_link=True, serialize=False)),
                ('recirc_content', models.ManyToManyField(related_name='liveblog_recirc', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
    ]
