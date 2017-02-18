# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-18 13:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ege', '0007_auto_20170218_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='exam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ege.Exam'),
        ),
        migrations.AlterField(
            model_name='task',
            name='order',
            field=models.IntegerField(help_text='Например: от 1 до 27', verbose_name='Номер задачи'),
        ),
    ]