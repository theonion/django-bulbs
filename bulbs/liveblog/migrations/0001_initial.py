# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

from bulbs.liveblog.utils import get_liveblog_author_model


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(get_liveblog_author_model()),
        migrations.swappable_dependency(settings.BULBS_LIVEBLOG_MODEL),
        ('content', '0012_auto_20160615_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveBlogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('headline', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
                ('authors', models.ManyToManyField(to=get_liveblog_author_model())),
                ('liveblog', models.ForeignKey(to=settings.BULBS_LIVEBLOG_MODEL, related_name='entries')),
                ('recirc_content', models.ManyToManyField(to='content.Content', related_name='liveblog_entry_recirc')),
            ],
        ),
        migrations.CreateModel(
            name='LiveBlogResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('ordering', models.IntegerField(null=True, blank=True, default=None)),
                ('body', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=get_liveblog_author_model())),
                ('entry', models.ForeignKey(to='liveblog.LiveBlogEntry', related_name='responses')),
            ],
        ),
    ]
