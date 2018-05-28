# Generated by Django 2.0.3 on 2018-03-06 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corefiles', '0008_auto_20171212_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('changed', models.DateTimeField(auto_now=True, db_index=True)),
                ('dirs', models.ManyToManyField(related_name='_fileset_dirs_+', to='corefiles.FileSet')),
                ('files', models.ManyToManyField(to='corefiles.File')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]