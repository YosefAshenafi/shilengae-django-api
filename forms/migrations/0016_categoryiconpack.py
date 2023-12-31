# Generated by Django 3.0 on 2021-11-21 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0015_formfieldimageresponse'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryIconPack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('icon', models.ImageField(upload_to='category_icon_packs')),
                ('version', models.IntegerField(default=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='icon', to='forms.Category')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
