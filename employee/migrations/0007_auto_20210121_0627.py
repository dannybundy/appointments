# Generated by Django 3.1.3 on 2021-01-21 14:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_auto_20210121_0627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
