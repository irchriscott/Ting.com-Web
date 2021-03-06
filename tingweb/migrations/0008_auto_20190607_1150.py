# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-07 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0007_auto_20190606_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='is_special',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='promotion',
            name='promotion_period',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
