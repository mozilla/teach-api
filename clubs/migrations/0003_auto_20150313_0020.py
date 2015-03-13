# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clubs', '0002_auto_20150313_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='creator',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, help_text=b'The user who created the Club.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='club',
            name='latitude',
            field=models.FloatField(help_text=b'Latitude of the club. Leave blank to automatically determine.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='club',
            name='longitude',
            field=models.FloatField(help_text=b'Longitude of the club.Leave blank to automatically determine.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
