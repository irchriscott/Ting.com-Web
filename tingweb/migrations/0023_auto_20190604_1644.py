# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-04 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0022_administratorresetpassword_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restauranttable',
            name='coordinates',
        ),
        migrations.AddField(
            model_name='restauranttable',
            name='description',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
