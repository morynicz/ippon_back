# Generated by Django 2.0.5 on 2018-06-02 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0007_tournament_finals_depth'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tournamentadmin',
            old_name='isMaster',
            new_name='is_master',
        ),
        migrations.RenameField(
            model_name='tournamentadmin',
            old_name='club',
            new_name='tournament',
        ),
    ]
