# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-06 05:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tingweb', '0002_branch_is_available'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=100)),
                ('occasion_event', models.CharField(max_length=200)),
                ('promotion_menu_type', models.CharField(max_length=100)),
                ('has_reduction', models.BooleanField(default=True)),
                ('amount', models.IntegerField(blank=True, default=0, null=True)),
                ('reduction_type', models.CharField(blank=True, max_length=100, null=True)),
                ('has_supplement', models.BooleanField(default=False)),
                ('supplement_max_quantity', models.IntegerField(default=1)),
                ('is_supplement_same', models.BooleanField(default=False)),
                ('supplement_quantity', models.IntegerField(default=1)),
                ('is_on', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now_add=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Administrator')),
                ('menu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu', to='tingweb.Menu')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Restaurant')),
                ('supplement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplement', to='tingweb.Menu')),
            ],
        ),
        migrations.CreateModel(
            name='PromotionInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_interested', models.BooleanField(default=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now_add=True)),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.Promotion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tingweb.User')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='has_promotion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tingweb.Promotion'),
        ),
    ]
