# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-01-15 19:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0028_auto_20200106_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='restaurant_type',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
