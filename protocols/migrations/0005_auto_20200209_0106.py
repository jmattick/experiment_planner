# Generated by Django 3.0.2 on 2020-02-09 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protocols', '0004_step_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='step',
            name='flexible',
        ),
        migrations.RemoveField(
            model_name='step',
            name='step_number',
        ),
    ]