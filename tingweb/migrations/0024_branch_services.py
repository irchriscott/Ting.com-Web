# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-12-28 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0023_restaurantconfig_user_should_pay_before'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='services',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]