# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='latitude',
            field=models.FloatField(help_text=b'Latitude of the club.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='club',
            name='longitude',
            field=models.FloatField(help_text=b'Longitude of the club.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
