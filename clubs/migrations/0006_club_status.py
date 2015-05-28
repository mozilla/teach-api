# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0005_auto_20150325_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='status',
            field=models.CharField(default=b'approved', help_text=b'Current approval status of the club.', max_length=10, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'denied', b'Denied')]),
            preserve_default=True,
        ),
    ]
