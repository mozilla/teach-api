# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs_guides', '0002_category_clubsguide'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clubsguide',
            name='translation_of',
            field=models.ForeignKey(related_name='translations', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='clubs_guides.ClubsGuide', help_text=b'The main guide that this guide is a translation of, if any', null=True),
            preserve_default=True,
        ),
    ]
