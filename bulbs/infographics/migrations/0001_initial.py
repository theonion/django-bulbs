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
            name='BaseInfographic',
            fields=[
                ('content_ptr', models.OneToOneField(primary_key=True, to='content.Content', parent_link=True, auto_created=True, serialize=False)),
                ('infographic_type', models.IntegerField(default=0)),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
    ]
