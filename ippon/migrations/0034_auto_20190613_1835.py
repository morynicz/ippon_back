# Generated by Django 2.2.1 on 2019-06-13 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ippon", "0033_auto_20190613_1821"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teamfight",
            name="result",
            field=models.IntegerField(choices=[(0, "None"), (1, "Aka"), (2, "Shiro")], default=0),
        ),
    ]
