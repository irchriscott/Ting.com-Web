# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-03-14 19:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0039_auto_20200313_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlacementMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('placement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Placement')),
            ],
        ),
    ]
