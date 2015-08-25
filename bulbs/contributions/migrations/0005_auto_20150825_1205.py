# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contributions', '0004_auto_20150825_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(default=0)),
                ('note', models.TextField()),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('contributor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='rate',
            name='name',
            field=models.IntegerField(null=True, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual'), (4, b'Override')]),
        ),
    ]
