# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveblog', '0002_liveblogresponse_internal_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='liveblogresponse',
            options={'ordering': ['ordering']},
        ),
    ]
