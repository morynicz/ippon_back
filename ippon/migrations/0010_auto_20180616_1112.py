# Generated by Django 2.0.5 on 2018-06-16 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0009_tournamentparticipation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tournamentparticipation',
            old_name='player_id',
            new_name='player',
        ),
        migrations.RenameField(
            model_name='tournamentparticipation',
            old_name='tournament_id',
            new_name='tournament',
        ),
        migrations.AlterField(
            model_name='tournamentparticipation',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tournamentparticipation',
            name='is_qualified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tournamentparticipation',
            name='is_registered',
            field=models.BooleanField(default=False),
        ),
    ]
