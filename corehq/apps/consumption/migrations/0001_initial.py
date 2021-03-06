# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-07 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SQLDefaultConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('domain', 'domain'),
                                                   ('product', 'product'),
                                                   ('supply-point-type', 'supply-point-type'),
                                                   ('supply-point', 'supply-point')],
                                          max_length=32,
                                          null=True)),
                ('domain', models.CharField(max_length=255, null=True)),
                ('product_id', models.CharField(max_length=126, null=True)),
                ('supply_point_type', models.CharField(max_length=126, null=True)),
                ('supply_point_id', models.CharField(max_length=126, null=True)),
                ('default_consumption', models.DecimalField(decimal_places=8, max_digits=64, null=True)),
                ('couch_id', models.CharField(db_index=True, max_length=126, null=True)),
            ],
            options={
                'db_table': 'consumption_defaultconsumption',
            },
        ),
    ]
