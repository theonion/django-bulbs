# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0003_auto_20150513_2326'),
        ('contributions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureTypeOverride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('rate', models.IntegerField(default=0)),
                ('feature_type', models.ForeignKey(related_name='overrides', to='content.FeatureType')),
            ],
        ),
        migrations.CreateModel(
            name='FreelanceProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_freelance', models.BooleanField(default=True)),
                ('payment_date', models.DateTimeField(null=True, blank=True)),
                ('contributor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
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
            name='Override',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(null=True, choices=[(0, b'Flat Rate'), (1, b'FeatureType'), (2, b'Hourly'), (3, b'Manual'), (4, b'Override')])),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('rate', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-updated_on',),
            },
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
                ('override_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Override')),
                ('contribution', models.ForeignKey(related_name='overrides', blank=True, to='contributions.Contribution', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.override',),
        ),
        migrations.CreateModel(
            name='FeatureTypeOverrideProfile',
            fields=[
                ('override_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Override')),
                ('feature_types', models.ManyToManyField(to='contributions.FeatureTypeOverride')),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.override',),
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
            model_name='override',
            name='contributor',
            field=models.ForeignKey(related_name='overrides', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='override',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_contributions.override_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='override',
            name='role',
            field=models.ForeignKey(related_name='overrides', to='contributions.ContributorRole', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='featuretyperate',
            unique_together=set([('role', 'feature_type')]),
        ),
    ]
