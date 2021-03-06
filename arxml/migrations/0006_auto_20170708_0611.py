# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-08 04:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arxml', '0005_package_proc_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connector',
            name='p_port',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='p_port_connector', to='arxml.Port'),
        ),
        migrations.AlterField(
            model_name='connector',
            name='r_port',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='r_port_connector', to='arxml.Port'),
        ),
    ]
