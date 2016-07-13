# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20160615_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSuperFeature',
            fields=[
                ('content_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='content.Content')),
                ('notes', models.TextField(default=b'', null=True, blank=True)),
                ('superfeature_type', models.CharField(max_length=255, choices=[(b'GUIDE_TO_HOMEPAGE', b'Guide To Homepage'), (b'GUIDE_TO_ENTRY', b'Guide To Entry')])),
                ('default_child_type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'GUIDE_TO_HOMEPAGE', b'Guide To Homepage'), (b'GUIDE_TO_ENTRY', b'Guide To Entry')])),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
        migrations.CreateModel(
            name='ContentRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordering', models.IntegerField()),
                ('child', models.ForeignKey(related_name='child', to='content.Content')),
                ('parent', models.ForeignKey(related_name='parent', to='content.Content')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contentrelation',
            unique_together=set([('parent', 'ordering')]),
        ),
    ]
