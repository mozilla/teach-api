# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0007_club_denial'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='affiliation',
            field=models.CharField(help_text=b'The affiliated institution or organization.', max_length=1000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='age_range',
            field=models.CharField(help_text=b'The club member age range.', max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='club_size',
            field=models.CharField(help_text=b'The number of club members.', max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='club_topics',
            field=models.CharField(help_text=b'Club topics/subjects.', max_length=1000, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='frequency',
            field=models.CharField(help_text=b'How frequently this club meets.', max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='hosting_reason',
            field=models.TextField(help_text=b'Reason to host a Mozilla club.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='how_they_heard',
            field=models.CharField(help_text=b'How did the applicant hear about Current approval status of the club.', max_length=100, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='member_occupation',
            field=models.CharField(help_text=b'Club member occupations.', max_length=1000, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='occupation',
            field=models.CharField(help_text=b"Club captain's occupation.", max_length=500, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='regional_coordinate',
            field=models.CharField(help_text=b'Regional Coordinator associated with club captain.', max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='venue',
            field=models.CharField(help_text=b'Where does this club meet.', max_length=1000, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='club',
            name='website',
            field=models.URLField(help_text=b"The URL of the club's primary website.", max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
