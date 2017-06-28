# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 19:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arxml', '0004_auto_20170627_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='softwarecomponent',
            name='name',
            field=models.CharField(default='SoftwareComponent', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='softwarecomponent',
            unique_together=set([('name', 'composition')]),
        ),
    ]