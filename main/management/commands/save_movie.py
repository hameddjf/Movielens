from django.core.management.base import BaseCommand
from main.utils import save_movie_details
import asyncio


class Command(BaseCommand):
    help = 'Save movie details to the database'

    def add_arguments(self, parser):
        parser.add_argument('movie_title', type=str,
                            help='The title of the movie to save')

    def handle(self, *args, **options):
        movie_title = options['movie_title']
        asyncio.run(save_movie_details(movie_title))
        self.stdout.write(self.style.SUCCESS(
            f"Successfully saved movie details for '{movie_title}'"))
