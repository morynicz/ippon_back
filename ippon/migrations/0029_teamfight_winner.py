# Generated by Django 2.1.4 on 2019-01-02 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ippon", "0028_auto_20190102_2013"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamfight",
            name="winner",
            field=models.IntegerField(choices=[(0, "None"), (1, "Aka"), (2, "Shiro")], default=0),
        ),
    ]
