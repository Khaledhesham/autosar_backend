# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-29 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arxml', '0012_auto_20170629_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='softwarecomponent',
            name='rte_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rte_file', to='files.File'),
        ),
    ]
