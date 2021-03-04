# Generated by Django 3.1.3 on 2021-01-28 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0010_auto_20210127_2229'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='length',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='service',
            name='price',
            field=models.IntegerField(),
        ),
    ]
