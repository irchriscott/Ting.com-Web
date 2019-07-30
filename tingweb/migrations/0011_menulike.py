# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-05 15:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0010_userresetpassword'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Menu')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.User')),
            ],
        ),
    ]