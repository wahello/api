# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-11 22:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ege', '0011_exam_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='time',
            field=models.IntegerField(blank=True, default=None, help_text='Отведённое время, мин', null=True),
        ),
    ]