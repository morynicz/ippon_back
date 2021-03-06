# Generated by Django 2.2.1 on 2019-06-04 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0031_auto_20190102_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='cupphase',
            name='number_of_positions',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='cupfight',
            name='team_fight',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cup_fight', to='ippon.TeamFight'),
        ),
    ]
