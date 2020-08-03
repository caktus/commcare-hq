# Generated by Django 1.11.7 on 2017-12-04 15:05
from corehq.sql_db.operations import RawSQLMigration
from django.db import migrations

from custom.icds_reports.const import SQL_TEMPLATES_ROOT

migrator = RawSQLMigration((SQL_TEMPLATES_ROOT,))


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0028_auto_20171204_1922'),
    ]

    operations = [
        migrator.get_migration('update_tables12.sql'),
    ]
