# Generated by Django 3.0 on 2021-12-18 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20210807_1946'),
        ('forms', '0016_categoryiconpack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='form',
            unique_together={('name', 'country')},
        ),
    ]
