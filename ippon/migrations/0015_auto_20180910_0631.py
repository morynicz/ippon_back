# Generated by Django 2.1.1 on 2018-09-10 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0014_auto_20180902_0840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='ippon.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together={('player', 'team')},
        ),
    ]
