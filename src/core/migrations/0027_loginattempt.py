# Generated by Django 2.0.2 on 2018-03-06 12:06

from django.db import migrations, models
import netfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_user_telegram_chat_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', netfields.fields.InetAddressField(max_length=39)),
                ('login', models.CharField(max_length=260)),
                ('password', models.CharField(max_length=260)),
            ],
        ),
    ]