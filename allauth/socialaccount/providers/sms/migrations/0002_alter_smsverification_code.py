# Generated by Django 5.1.6 on 2025-02-18 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsverification',
            name='code',
            field=models.CharField(),
        ),
    ]
