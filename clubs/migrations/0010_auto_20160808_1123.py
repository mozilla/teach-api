# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0009_auto_20160802_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='denial',
            field=models.CharField(default=b'pending', help_text=b'Reason for denial, if denied.', max_length=50, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'no longer interested', b'No longer interested'), (b'not qualified', b'Not qualified'), (b'no response', b'No response after initial application'), (b'cannot be emailed', b'Applicant cannot be emailed')]),
            preserve_default=True,
        ),
    ]
