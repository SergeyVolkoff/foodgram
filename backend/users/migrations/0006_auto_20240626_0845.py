# Generated by Django 2.2.16 on 2024-06-26 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240626_0755'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Follow',
            new_name='Subscriptions',
        ),
    ]
