# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-21 09:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0040_placementmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=18),
        ),
    ]
