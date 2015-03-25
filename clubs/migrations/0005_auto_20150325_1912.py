# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0004_auto_20150313_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='website',
            field=models.URLField(help_text=b"The URL of the club's primary website.", blank=True),
            preserve_default=True,
        ),
    ]
