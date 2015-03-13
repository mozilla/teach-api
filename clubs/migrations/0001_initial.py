# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'The name of the club.', max_length=100)),
                ('website', models.URLField(help_text=b"The URL of the club's primary website.")),
                ('description', models.TextField(help_text=b'Description of the club.')),
                ('location', models.CharField(help_text=b'Location of the club (city or country).', max_length=100)),
                ('latitude', models.FloatField(help_text=b'Latitude of the club.')),
                ('longitude', models.FloatField(help_text=b'Longitude of the club.')),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this club should be treated as active. Unselect this instead of deleting clubs.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
