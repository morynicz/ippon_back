# Generated by Django 3.0.4 on 2020-04-05 17:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ippon', '0042_auto_20200405_1406'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventAdmins',
            new_name='EventAdmin',
        ),
    ]