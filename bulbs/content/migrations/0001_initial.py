# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations
from django.conf import settings
import djbetty.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    
    if django.VERSION >= (1, 8, 0):
        dependencies.insert(0,
            ('contenttypes', '0002_remove_content_type_name'))

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=512)),
                ('slug', models.SlugField(default=b'', blank=True)),
                ('description', models.TextField(default=b'', max_length=1024, blank=True)),
                ('thumbnail_override', djbetty.fields.ImageField(default=None, null=True, editable=False, blank=True)),
                ('subhead', models.CharField(default=b'', max_length=255, blank=True)),
                ('indexed', models.BooleanField(default=True)),
                ('authors', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('publish_own_content', 'Can publish their own content'), ('publish_content', 'Can publish content'), ('promote_content', 'Can promote content')),
            },
        ),
        migrations.CreateModel(
            name='FeatureType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_time', models.DateTimeField(auto_now=True, verbose_name=b'action time')),
                ('object_id', models.TextField(null=True, verbose_name=b'object id', blank=True)),
                ('change_message', models.TextField(verbose_name=b'change message', blank=True)),
                ('content_type', models.ForeignKey(related_name='change_logs', blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(related_name='change_logs', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-action_time',),
            },
        ),
        migrations.CreateModel(
            name='ObfuscatedUrlInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_date', models.DateTimeField()),
                ('expire_date', models.DateTimeField()),
                ('url_uuid', models.CharField(unique=True, max_length=32, editable=False)),
                ('content', models.ForeignKey(to='content.Content')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_content.tag_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='content',
            name='feature_type',
            field=models.ForeignKey(blank=True, to='content.FeatureType', null=True),
        ),
        migrations.AddField(
            model_name='content',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_content.content_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='content',
            name='tags',
            field=models.ManyToManyField(to='content.Tag', blank=True),
        ),
    ]
