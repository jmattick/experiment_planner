# Generated by Django 3.0.2 on 2020-03-05 21:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('protocols', '0007_auto_20200305_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
