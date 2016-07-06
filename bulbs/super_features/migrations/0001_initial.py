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
                ('notes', models.TextField()),
                ('superfeature_type', models.CharField(max_length=255, choices=[(b'GUIDE_TO', b'Guide To')])),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content', models.Model),
        ),
    ]
