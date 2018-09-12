# Generated by Django 2.0.5 on 2018-08-31 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0011_auto_20180616_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teams', to='ippon.Tournament')),
            ],
        ),
        migrations.CreateModel(
            name='TeamFight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aka_team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ippon.Team')),
                ('shiro_team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ippon.Team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='team_fights', to='ippon.Tournament')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ippon.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='members', to='ippon.Team')),
            ],
        ),
    ]