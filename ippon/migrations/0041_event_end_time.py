# Generated by Django 3.0.4 on 2020-04-02 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0040_auto_20200401_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
