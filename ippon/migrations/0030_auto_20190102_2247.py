# Generated by Django 2.1.4 on 2019-01-02 22:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ippon", "0029_teamfight_winner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cupfight",
            name="team_fight",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="cup_fight",
                to="ippon.TeamFight",
            ),
        ),
        migrations.AlterField(
            model_name="groupfight",
            name="team_fight",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="group_fight",
                to="ippon.TeamFight",
            ),
        ),
    ]
