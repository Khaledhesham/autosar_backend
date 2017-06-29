# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-29 17:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0012_auto_20170629_1517'),
        ('arxml', '0009_auto_20170629_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='softwarecomponent',
            name='child_directory',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='files.Directory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='softwarecomponent',
            name='datatypes_file',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='datatypes_file', to='files.File'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='softwarecomponent',
            name='rte_datatypes_file',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='rte_datatypes_file', to='files.File'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='softwarecomponent',
            name='rte_file',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='rte__file', to='files.File'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='softwarecomponent',
            name='runnables_file',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='runnables_file', to='files.File'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='softwarecomponent',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file', to='files.File'),
        ),
    ]
