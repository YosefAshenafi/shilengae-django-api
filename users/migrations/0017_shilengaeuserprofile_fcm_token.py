# Generated by Django 3.0 on 2022-02-16 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_shilengaeuser_v1_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='shilengaeuserprofile',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]