# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 22:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arxml', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatype',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arxml.Package'),
        ),
    ]
