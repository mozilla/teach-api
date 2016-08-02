# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0008_auto_20160725_1605'),
    ]

    operations = [
        migrations.RenameField(
            model_name='club',
            old_name='regional_coordinate',
            new_name='regional_coordinator',
        ),
        migrations.AddField(
            model_name='club',
            name='intent',
            field=models.CharField(default=b'start', help_text=b'Is this for starting a new club or connecting an existing club?', max_length=100),
            preserve_default=True,
        ),
    ]
