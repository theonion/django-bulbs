# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
        ('testcontent', '0011_testliveblog'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveBlogEntry',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('published', models.DateTimeField(blank=True, null=True)),
                ('headline', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
                ('authors', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('liveblog', models.ForeignKey(related_name='entries', to='testcontent.TestLiveBlog')),
                ('recirc_content', models.ManyToManyField(related_name='liveblog_entry_recirc', to='content.Content')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ordering', models.IntegerField(blank=True, default=None, null=True)),
                ('body', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('entry', models.ForeignKey(related_name='responses', to='liveblog.LiveBlogEntry')),
            ],
        ),
    ]
