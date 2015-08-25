# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contributions', '0002_auto_20150629_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleRateOverride',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('contributor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(related_name='rate_override', to='contributions.ContributorRole')),
            ],
            bases=('contributions.rate',),
        ),
    ]
