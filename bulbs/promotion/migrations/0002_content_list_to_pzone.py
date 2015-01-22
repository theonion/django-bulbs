# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('content', '0001_initial'),
        ('promotion', '0001_initial'),
    ]

    operations = [

        # cleanup old models
        migrations.DeleteModel(
            name='LockOperation',
        ),
        migrations.DeleteModel(
            name='UnlockOperation',
        ),
        migrations.DeleteModel(
            name='InsertOperation'
        ),
        migrations.DeleteModel(
            name='ReplaceOperation'
        ),
        migrations.DeleteModel(
            name='ContentListOperation'
        ),
        migrations.DeleteModel(
            name='ContentListHistory',
        ),

        # fix up content list which is now pzone
        migrations.RenameModel(
            old_name='ContentList',
            new_name='PZone',
        ),
        migrations.RenameField(
            model_name='pzone',
            old_name='length',
            new_name='zone_length',
        ),

        # pzone operation modifications
        migrations.CreateModel(
            name='PZoneOperation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
                ('applied', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-when', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pzoneoperation',
            name='content',
            field=models.ForeignKey(related_name='+', to='content.Content'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pzoneoperation',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_promotion.pzoneoperation_set', editable=False, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pzoneoperation',
            name='pzone',
            field=models.ForeignKey(related_name='operations', to='promotion.PZone'),
            preserve_default=True,
        ),

        # delete operation modifications
        migrations.CreateModel(
            name='DeleteOperation',
            fields=[
                ('pzoneoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.PZoneOperation')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.pzoneoperation',),
        ),

        # insert operation modifications
        migrations.CreateModel(
            name='InsertOperation',
            fields=[
                ('pzoneoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.PZoneOperation')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.pzoneoperation',),
        ),
        migrations.AddField(
            model_name='insertoperation',
            name='index',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),

        # replace operation modifications
        migrations.CreateModel(
            name='ReplaceOperation',
            fields=[
                ('pzoneoperation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='promotion.PZoneOperation')),
            ],
            options={
                'abstract': False,
            },
            bases=('promotion.pzoneoperation',),
        ),
        migrations.AddField(
            model_name='replaceoperation',
            name='index',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),

        # pzone history modifications
        migrations.CreateModel(
            name='PZoneHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', json_field.fields.JSONField(default=[], help_text='Enter a valid JSON object')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pzonehistory',
            name='pzone',
            field=models.ForeignKey(related_name='history', to='promotion.PZone'),
            preserve_default=True,
        ),
    ]
