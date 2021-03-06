# Generated by Django 2.1.1 on 2018-10-22 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0018_auto_20180920_1901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_member', to='ippon.Player'),
        ),
        migrations.AlterField(
            model_name='tournamentadmin',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admins', to='ippon.Tournament'),
        ),
    ]
