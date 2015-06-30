# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20150513_2326'),
        ('contributions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(default=3, max_length=255, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual'), (4, b'Override')])),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('rate', models.IntegerField()),
            ],
            options={
                'ordering': ('-updated_on',),
            },
        ),
        migrations.AddField(
            model_name='contribution',
            name='minutes_worked',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='payment_type',
            field=models.IntegerField(default=3, max_length=255, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual')]),
        ),
        migrations.CreateModel(
            name='ContributionRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('contribution', models.ForeignKey(related_name='rates', to='contributions.Contribution')),
            ],
            bases=('contributions.rate',),
        ),
        migrations.CreateModel(
            name='ContributorRoleRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('role', models.ForeignKey(related_name='rates', to='contributions.ContributorRole')),
            ],
            bases=('contributions.rate',),
        ),
        migrations.CreateModel(
            name='FeatureTypeRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('feature_type', models.ForeignKey(related_name='rates', to='content.FeatureType')),
            ],
            bases=('contributions.rate',),
        ),
    ]
