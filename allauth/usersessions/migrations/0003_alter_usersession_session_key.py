# Generated by Django 5.1.6 on 2025-02-25 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersessions', '0002_alter_usersession_session_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersession',
            name='session_key',
            field=models.TextField(editable=False, unique=True, verbose_name='session key'),
        ),
    ]
