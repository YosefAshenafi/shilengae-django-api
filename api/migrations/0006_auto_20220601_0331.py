# Generated by Django 3.0 on 2022-06-01 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20220410_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appversion',
            name='app_version',
            field=models.CharField(max_length=10),
        ),
    ]
