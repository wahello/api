# Generated by Django 2.0.1 on 2018-01-13 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0030_auto_20180111_1646'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='faculty',
            unique_together={('title', 'university')},
        ),
    ]
