# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-30 19:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0003_categoryrestaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrator',
            name='restaurant',
            field=models.ForeignKey(default='0712345678', on_delete=django.db.models.deletion.CASCADE, to='tingweb.Restaurant'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurantconfig',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
