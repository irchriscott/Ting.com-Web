# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-24 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0022_restaurantconfig_can_take_away'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurantconfig',
            name='user_should_pay_before',
            field=models.BooleanField(default=False),
        ),
    ]
