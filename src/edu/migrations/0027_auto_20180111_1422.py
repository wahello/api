# Generated by Django 2.0.1 on 2018-01-11 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0026_auto_20180111_1406'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='faculty',
            unique_together={('code', 'university'), ('title', 'university')},
        ),
    ]
