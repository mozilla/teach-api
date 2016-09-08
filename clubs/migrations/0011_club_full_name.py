# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0010_auto_20160808_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='full_name',
            field=models.CharField(help_text=b'Full name for the Club captain for this club.', max_length=200, null=True),
            preserve_default=True,
        ),
    ]
