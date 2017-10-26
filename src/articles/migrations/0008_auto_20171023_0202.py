# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-22 23:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_article_cut'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='description',
            field=models.TextField(blank=True, default=None, help_text='2–4 предложения под заголовком публикации в соцсетях.', null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, default=None, editable=False, help_text='Use in URLs like: /articles/.../how-to-install-linux', max_length=765, null=True, verbose_name='In URL'),
        ),
    ]
