# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-21 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0009_auto_20170619_0017'),
    ]

    operations = [
        migrations.AddField(
            model_name='arxmlfile',
            name='x',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='arxmlfile',
            name='y',
            field=models.IntegerField(default=0),
        ),
    ]