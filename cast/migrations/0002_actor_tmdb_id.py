# Generated by Django 5.0 on 2024-04-05 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cast', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='tmdb_id',
            field=models.IntegerField(null=True, unique=True, verbose_name='TMDB ID'),
        ),
    ]
