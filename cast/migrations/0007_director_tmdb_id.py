# Generated by Django 5.0 on 2024-04-14 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cast', '0006_alter_actor_movies'),
    ]

    operations = [
        migrations.AddField(
            model_name='director',
            name='tmdb_id',
            field=models.IntegerField(default='1', unique=True, verbose_name='شناسه TMDB کارگردان'),
        ),
    ]
