# Generated by Django 5.0 on 2024-04-05 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cast', '0004_director_poster'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
