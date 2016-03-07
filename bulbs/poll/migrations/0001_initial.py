# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_content_evergreen'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sodahead_answer_id', models.CharField(default=b'', max_length=20, blank=True)),
                ('answer_text', models.TextField(default=b'', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('question_text', models.TextField(default=b'', blank=True)),
                ('sodahead_id', models.CharField(default=b'', max_length=20, blank=True)),
                ('last_answer_index', models.IntegerField(default=0)),
                ('end_date', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.AddField(
            model_name='answer',
            name='poll',
            field=models.ForeignKey(related_name='answers', to='poll.Poll'),
        ),
    ]
