# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCategory',
            fields=[
                ('tag_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Tag')),
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
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='TestContentDetailImage',
            fields=[
                ('testcontentobj_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='testcontent.TestContentObj')),
                ('detail_caption', models.CharField(max_length=255, null=True, editable=False, blank=True)),
                ('detail_alt', models.CharField(max_length=255, null=True, editable=False, blank=True)),
                ('detail_image', djbetty.fields.ImageField(default=None, alt_field=b'detail_alt', null=True, caption_field=b'detail_caption', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('testcontent.testcontentobj',),
        ),
        migrations.CreateModel(
            name='TestContentObjTwo',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('foo', models.CharField(max_length=255)),
                ('bar', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
    ]
