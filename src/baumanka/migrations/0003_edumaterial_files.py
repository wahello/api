# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corefiles', '0007_auto_20170908_2348'),
        ('baumanka', '0002_remove_edumaterial_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='edumaterial',
            name='files',
            field=models.ManyToManyField(to='corefiles.File'),
        ),
    ]
