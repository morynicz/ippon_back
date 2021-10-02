# Generated by Django 2.2.1 on 2019-06-13 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ippon", "0036_teamfight_is_started"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="teamfight",
            name="is_started",
        ),
        migrations.AddField(
            model_name="teamfight",
            name="status",
            field=models.IntegerField(choices=[(0, "Prepared"), (1, "Started"), (2, "Finished")], default=0),
        ),
    ]
