# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0003_auto_20150513_2326'),
        ('contributions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseOverride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.IntegerField(default=0)),
                ('updated_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-updated_on',),
            },
        ),
        migrations.CreateModel(
            name='FreelanceProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_freelance', models.BooleanField(default=True)),
                ('is_manager', models.BooleanField(default=True)),
                ('payment_date', models.DateTimeField(null=True, blank=True)),
                ('contributor', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(default=0)),
                ('note', models.TextField()),
                ('payment_date', models.DateTimeField(null=True, blank=True)),
                ('contributor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OverrideProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contributor', models.ForeignKey(related_name='overrides', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(null=True, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual'), (4, b'Override')])),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('rate', models.IntegerField()),
            ],
            options={
                'ordering': ('-updated_on',),
            },
        ),
        migrations.AddField(
            model_name='contribution',
            name='force_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contribution',
            name='minutes_worked',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='contribution',
            name='payment_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='contributorrole',
            name='payment_type',
            field=models.IntegerField(default=3, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual')]),
        ),
        migrations.AlterField(
            model_name='contribution',
            name='content',
            field=models.ForeignKey(related_name='contributions', to='content.Content'),
        ),
        migrations.AlterField(
            model_name='contribution',
            name='contributor',
            field=models.ForeignKey(related_name='contributions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ContributionOverride',
            fields=[
                ('baseoverride_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.BaseOverride')),
                ('contribution', models.ForeignKey(related_name='override_contribution', to='contributions.Contribution')),
            ],
            bases=('contributions.baseoverride',),
        ),
        migrations.CreateModel(
            name='FeatureTypeOverride',
            fields=[
                ('baseoverride_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.BaseOverride')),
                ('feature_type', models.ForeignKey(to='content.FeatureType')),
            ],
            bases=('contributions.baseoverride',),
        ),
        migrations.CreateModel(
            name='FeatureTypeRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('feature_type', models.ForeignKey(related_name='feature_type_rates', to='content.FeatureType')),
                ('role', models.ForeignKey(related_name='feature_type_rates', to='contributions.ContributorRole', null=True)),
            ],
            bases=('contributions.rate',),
        ),
        migrations.CreateModel(
            name='FlatRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('role', models.ForeignKey(related_name='flat_rates', to='contributions.ContributorRole')),
            ],
            bases=('contributions.rate',),
        ),
        migrations.CreateModel(
            name='FlatRateOverride',
            fields=[
                ('baseoverride_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.BaseOverride')),
            ],
            bases=('contributions.baseoverride',),
        ),
        migrations.CreateModel(
            name='HourlyOverride',
            fields=[
                ('baseoverride_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.BaseOverride')),
            ],
            bases=('contributions.baseoverride',),
        ),
        migrations.CreateModel(
            name='HourlyRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('role', models.ForeignKey(related_name='hourly_rates', to='contributions.ContributorRole')),
            ],
            bases=('contributions.rate',),
        ),
        migrations.CreateModel(
            name='ManualRate',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
                ('contribution', models.ForeignKey(related_name='manual_rates', to='contributions.Contribution')),
            ],
            bases=('contributions.rate',),
        ),
        migrations.AddField(
            model_name='overrideprofile',
            name='role',
            field=models.ForeignKey(related_name='overrides', to='contributions.ContributorRole'),
        ),
        migrations.AlterUniqueTogether(
            name='overrideprofile',
            unique_together=set([('contributor', 'role')]),
        ),
        migrations.AddField(
            model_name='hourlyoverride',
            name='profile',
            field=models.ForeignKey(related_name='override_hourly', to='contributions.OverrideProfile'),
        ),
        migrations.AddField(
            model_name='flatrateoverride',
            name='profile',
            field=models.ForeignKey(related_name='override_flatrate', to='contributions.OverrideProfile'),
        ),
        migrations.AddField(
            model_name='featuretypeoverride',
            name='profile',
            field=models.ForeignKey(related_name='override_feature_type', to='contributions.OverrideProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='featuretyperate',
            unique_together=set([('role', 'feature_type')]),
        ),
    ]
