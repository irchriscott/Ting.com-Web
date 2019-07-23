# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-23 07:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0019_auto_20190721_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_type', models.IntegerField()),
                ('from_id', models.IntegerField()),
                ('message', models.CharField(max_length=255)),
                ('notif_type', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.User')),
            ],
        ),
    ]
