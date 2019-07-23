# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-23 08:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0020_usernotification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='is_accepted',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='is_canceled',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='is_complete',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='is_refunded',
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.IntegerField(default=1),
        ),
    ]
