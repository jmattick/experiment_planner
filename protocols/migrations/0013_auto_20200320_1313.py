# Generated by Django 3.0.2 on 2020-03-20 18:13

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('protocols', '0012_auto_20200320_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateField(default=datetime.datetime(2020, 3, 20, 18, 13, 57, 79725, tzinfo=utc)),
        ),
    ]
