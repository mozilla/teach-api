# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs_guides', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClubsGuide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'The descriptive title for the club guide', max_length=150)),
                ('url', models.URLField(help_text=b"Website link to the guide's content", max_length=500)),
                ('language', models.CharField(help_text=b'The language this guide is in', max_length=150, null=True, blank=True)),
                ('category', models.ForeignKey(related_name='clubs_guides', to='clubs_guides.Category', help_text=b'Clubs Guide category this guide belongs to')),
                ('translation_of', models.ForeignKey(related_name='translations', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='clubs_guides.ClubsGuide', help_text=b'If this is a guide that has been translated from another guide (blank if this is the main guide)', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
