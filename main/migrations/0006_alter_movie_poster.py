# Generated by Django 5.0 on 2024-04-05 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_movie_tmdb_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to='movies/', verbose_name='پوستر'),
        ),
    ]
