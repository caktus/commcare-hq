# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-10 21:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_auth', '0002_populate_sql'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SQLMobileAuthKeyRecord',
            new_name='MobileAuthKeyRecord',
        ),
        migrations.AlterModelTable(
            name='mobileauthkeyrecord',
            table=None,
        ),
    ]