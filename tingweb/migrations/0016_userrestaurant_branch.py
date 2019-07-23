# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-19 16:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0015_restaurantreview_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrestaurant',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Branch'),
            preserve_default=False,
        ),
    ]
