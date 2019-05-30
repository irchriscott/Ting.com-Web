# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-28 02:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0019_auto_20190515_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResetPassword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=200)),
                ('token', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expired_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.User')),
            ],
        ),
    ]
