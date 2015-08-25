# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0003_auto_20150513_2326'),
        ('contributions', '0005_auto_20150825_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='Override',
            fields=[
                ('rate_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Rate')),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.rate', models.Model),
        ),
        migrations.RemoveField(
            model_name='rolerateoverride',
            name='contributor',
        ),
        migrations.RemoveField(
            model_name='rolerateoverride',
            name='rate_ptr',
        ),
        migrations.RemoveField(
            model_name='rolerateoverride',
            name='role',
        ),
        migrations.CreateModel(
            name='FeatureTypeOverride',
            fields=[
                ('override_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Override')),
                ('feature_type', models.ForeignKey(related_name='overrides', to='content.FeatureType')),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.override',),
        ),
        migrations.CreateModel(
            name='RoleOverride',
            fields=[
                ('override_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.Override')),
                ('role', models.ForeignKey(related_name='overrides', to='contributions.ContributorRole')),
            ],
            options={
                'abstract': False,
            },
            bases=('contributions.override',),
        ),
        migrations.DeleteModel(
            name='RoleRateOverride',
        ),
        migrations.AddField(
            model_name='override',
            name='contributor',
            field=models.ForeignKey(related_name='overrides', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='override',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_contributions.override_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
