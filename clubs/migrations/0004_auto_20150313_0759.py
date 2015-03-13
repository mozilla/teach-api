# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clubs', '0003_auto_20150313_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='creator',
        ),
        migrations.AddField(
            model_name='club',
            name='owner',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, help_text=b'The user who owns the Club and can change it.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='club',
            name='longitude',
            field=models.FloatField(help_text=b'Longitude of the club. Leave blank to automatically determine.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
