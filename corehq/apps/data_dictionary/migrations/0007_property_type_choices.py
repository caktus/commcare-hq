# Generated by Django 1.10.5 on 2017-03-02 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_dictionary', '0006_caseproperty_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseproperty',
            name='data_type',
            field=models.CharField(blank=True, choices=[('date', 'Date'), ('plain', 'Plain'), ('number', 'Number'), ('select', 'Select'), ('barcode', 'Barcode'), ('gps', 'GPS'), ('phone_number', 'Phone Number'), ('password', 'Password'), ('', 'No Type Currently Selected')], default='', max_length=20),
        ),
    ]
