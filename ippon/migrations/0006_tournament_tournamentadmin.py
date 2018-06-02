# Generated by Django 2.0.5 on 2018-05-24 18:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ippon', '0005_auto_20180415_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('webpage', models.URLField()),
                ('description', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('address', models.CharField(max_length=500)),
                ('team_size', models.IntegerField()),
                ('group_match_length', models.IntegerField()),
                ('ko_match_length', models.IntegerField()),
                ('final_match_length', models.IntegerField()),
                ('age_constraint', models.IntegerField(choices=[(0, 'None'), (1, 'Less'), (2, 'LessOrEqual'), (3, 'Greater'), (4, 'GreateOrEqual'), (5, 'Equal'), (6, 'NotEqual')])),
                ('rank_constraint', models.IntegerField(choices=[(0, 'None'), (1, 'Less'), (2, 'LessOrEqual'), (3, 'Greater'), (4, 'GreateOrEqual'), (5, 'Equal'), (6, 'NotEqual')])),
                ('sex_constraint', models.IntegerField(choices=[(0, 'None'), (1, 'WomenOnly'), (2, 'MenOnly')])),
                ('rank_constraint_value', models.IntegerField(choices=[(0, 'None'), (1, 'Kyu_6'), (2, 'Kyu_5'), (3, 'Kyu_4'), (4, 'Kyu_3'), (5, 'Kyu_2'), (6, 'Kyu_1'), (7, 'Dan_1'), (8, 'Dan_2'), (9, 'Dan_3'), (10, 'Dan_4'), (11, 'Dan_5'), (12, 'Dan_6'), (13, 'Dan_7'), (14, 'Dan_8')])),
                ('age_constraint_value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TournamentAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isMaster', models.BooleanField()),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='admins', to='ippon.Tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tournaments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
