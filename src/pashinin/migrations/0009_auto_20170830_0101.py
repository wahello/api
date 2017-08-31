# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-29 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pashinin', '0008_auto_20170829_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='courselead',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courselead',
            name='contact',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='courselead',
            name='name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Name'),
        ),
    ]
