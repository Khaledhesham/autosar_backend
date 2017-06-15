# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-15 12:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('files', '0004_auto_20170514_1953'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Autosar', max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Created')),
            ],
            options={
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.AddField(
            model_name='directory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='files.Directory'),
        ),
        migrations.AlterField(
            model_name='file',
            name='saved_file',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='project',
            name='directory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.Directory'),
        ),
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
