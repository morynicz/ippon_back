# Generated by Django 2.1.1 on 2018-10-25 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0019_auto_20181022_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='ippon.Tournament')),
            ],
        ),
    ]
