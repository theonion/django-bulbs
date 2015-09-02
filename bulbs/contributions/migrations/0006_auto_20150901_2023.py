# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contributions', '0005_auto_20150831_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreelanceProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_date', models.DateTimeField(null=True, blank=True)),
                ('contributor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='contribution',
            name='contributor',
            field=models.ForeignKey(related_name='contributions', to=settings.AUTH_USER_MODEL),
        ),
    ]
