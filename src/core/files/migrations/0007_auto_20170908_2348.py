# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 20:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corefiles', '0006_auto_20170908_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='basefile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='corefiles.BaseFile'),
        ),
    ]
