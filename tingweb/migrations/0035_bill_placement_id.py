# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-24 10:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0034_order_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='placement_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
