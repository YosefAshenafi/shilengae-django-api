# Generated by Django 3.0 on 2021-10-20 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_reportedads'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='promoted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ad',
            name='promotedExpiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
