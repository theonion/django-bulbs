# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0003_auto_20150826_2250'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributionOverride',
            fields=[
                ('override_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Override')),
                ('contribution', models.ForeignKey(related_name='overrides', blank=True, to='contributions.Contribution', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.override',),
        ),
        migrations.AlterField(
            model_name='override',
            name='contributor',
            field=models.ForeignKey(related_name='overrides', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='override',
            name='role',
            field=models.ForeignKey(related_name='overrides', to='contributions.ContributorRole', null=True),
        ),
    ]
