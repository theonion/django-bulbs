# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
                ('length', models.IntegerField(default=10)),
                ('data', json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContentListHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('content_list', models.ForeignKey(related_name='history', to='promotion.ContentList')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContentListOperation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
                ('applied', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-when'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InsertOperation',
            fields=[
                ('contentlistoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.ContentListOperation')),
                ('index', models.IntegerField(default=0)),
                ('lock', models.BooleanField(default=False)),
                ('content', models.ForeignKey(related_name='+', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.contentlistoperation',),
        ),
        migrations.CreateModel(
            name='LockOperation',
            fields=[
                ('contentlistoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.ContentListOperation')),
                ('target', models.ForeignKey(related_name='+', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.contentlistoperation',),
        ),
        migrations.CreateModel(
            name='ReplaceOperation',
            fields=[
                ('contentlistoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.ContentListOperation')),
                ('lock', models.BooleanField(default=False)),
                ('content', models.ForeignKey(related_name='+', to='content.Content')),
                ('target', models.ForeignKey(related_name='+', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.contentlistoperation',),
        ),
        migrations.CreateModel(
            name='UnlockOperation',
            fields=[
                ('contentlistoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.ContentListOperation')),
                ('target', models.ForeignKey(related_name='+', to='content.Content')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.contentlistoperation',),
        ),
        migrations.AddField(
            model_name='contentlistoperation',
            name='content_list',
            field=models.ForeignKey(related_name='operations', to='promotion.ContentList'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contentlistoperation',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_promotion.contentlistoperation_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
    ]
