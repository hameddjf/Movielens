# Generated by Django 5.0 on 2024-04-05 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_rename_category_movie_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='tmdb_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]