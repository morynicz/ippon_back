# Generated by Django 2.2.1 on 2019-06-13 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ippon', '0037_auto_20190613_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='fight',
            name='status',
            field=models.IntegerField(choices=[(0, 'Prepared'), (1, 'Started'), (2, 'Finished')], default=0),
        ),
        migrations.AddField(
            model_name='fight',
            name='winner',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'Aka'), (2, 'Shiro')], default=0),
        ),
    ]
