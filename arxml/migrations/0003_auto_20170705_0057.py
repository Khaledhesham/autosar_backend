# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 22:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arxml', '0002_auto_20170705_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arxml.Package'),
        ),
    ]
