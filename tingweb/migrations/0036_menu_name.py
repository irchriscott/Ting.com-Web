# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-27 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0035_bill_placement_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
