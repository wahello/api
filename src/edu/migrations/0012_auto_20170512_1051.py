# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-12 10:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0011_auto_20170512_1041'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tag',
            new_name='Category',
        ),
    ]