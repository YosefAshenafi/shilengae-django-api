# Generated by Django 3.0 on 2021-10-01 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20211001_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='shilengaeuser',
            name='is_guest',
            field=models.BooleanField(default=False),
        ),
    ]
