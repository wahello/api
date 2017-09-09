# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-09 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20170907_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='browser_on_creation',
            field=models.CharField(blank=True, db_index=True, default=None, help_text='Browser string used when this user was created', max_length=200, null=True),
        ),
    ]
