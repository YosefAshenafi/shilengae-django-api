# Generated by Django 3.0 on 2021-10-25 19:21

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0013_auto_20211007_0210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='formfieldresponse',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
    ]
