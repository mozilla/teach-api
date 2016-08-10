# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('credly', '0002_usercredlyprofile_token_refreshed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercredlyprofile',
            name='token_refreshed',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True),
            preserve_default=True,
        ),
    ]
