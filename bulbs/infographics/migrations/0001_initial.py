# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_auto_20160606_1004'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseInfographic',
            fields=[
                ('content_ptr', models.OneToOneField(serialize=False, to='content.Content', primary_key=True, auto_created=True, parent_link=True)),
                ('infographic_type', models.IntegerField(default=0)),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
            bases=('content.content',),
        ),
    ]
