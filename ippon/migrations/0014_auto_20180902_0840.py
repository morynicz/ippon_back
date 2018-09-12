# Generated by Django 2.0.5 on 2018-09-02 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0013_team_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering_number', models.IntegerField(default=0)),
                ('aka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='ippon.Player')),
                ('shiro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='ippon.Player')),
                ('team_fight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ippon.TeamFight')),
            ],
        ),
        migrations.AlterField(
            model_name='team',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='ippon.Tournament'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ippon.Player'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='ippon.Team'),
        ),
    ]