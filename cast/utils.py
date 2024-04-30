import os
import requests

from django.db import transaction
from django.utils.text import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import Actor, Director

from main.models import Movie, Genre

# آدرس پایه API
BASE_URL = "https://api.themoviedb.org/3/"
tmdb_api_key = settings.TMDB_API_KEY


def get_or_create_actor(actor_name):
    try:
        actor = Actor.objects.get(name=actor_name)
    except Actor.DoesNotExist:
        actor = Actor.objects.create(
            name=actor_name, poster=f'actors/{slugify(actor_name)}.jpg')
    return actor


def save_actor_image(self, actor_name):
    tmdb_api_key = settings.TMDB_API_KEY
    search_url = f'https://api.themoviedb.org/3/search/person?api_key={
        tmdb_api_key}&query={actor_name}'
    search_response = requests.get(search_url)

    if search_response.status_code == 200:
        search_results = search_response.json().get('results', [])
        if search_results:
            actor_data = search_results[0]
            profile_path = actor_data.get('profile_path')
            if profile_path:
                image_url = f'https://image.tmdb.org/t/p/w500{profile_path}'

                file_name = f"{slugify(actor_name)}.jpg"
                file_path = os.path.join('actors/', file_name)

                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        if not default_storage.exists(file_path):
                            actor = get_or_create_actor(actor_name)
                            actor.poster = file_path
                            actor.save()
                            default_storage.save(
                                file_path, ContentFile(response.content))
                            self.stdout.write(self.style.SUCCESS(
                                f'File {file_name} downloaded and saved at {file_path}.'))
                        else:
                            self.stdout.write(
                                f'File {file_name} already exists at {file_path}.')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Failed to download image for {actor_name}: {e}'))
    else:
        self.stdout.write(self.style.WARNING(
            f'No image found for actor "{actor_name}".'))


def save_movie_poster(movie, image_url):
    """ذخیره تصویر فیلم در پوشه 'movies'"""
    file_name = f"{slugify(movie.title)}.jpg"
    file_path = os.path.join('movies/', file_name)

    response = requests.get(image_url)
    if response.status_code == 200:
        if not default_storage.exists(file_path):
            default_storage.save(file_path, ContentFile(response.content))
            movie.poster.save(file_name, ContentFile(
                response.content), save=True)
            print(f'File {file_name} downloaded and saved at {file_path}.')
        else:
            print(f'File {file_name} already exists at {file_path}.')
    else:
        print(f'Failed to download image for movie {movie.title}.')


def download_actor_images_and_get_movie_info(actor_names, tmdb_api_key):
    """دانلود تصاویر بازیگران و دریافت اطلاعات فیلم‌ها"""
    for name in actor_names:
        search_url = f'https://api.themoviedb.org/3/search/person?api_key={
            tmdb_api_key}&language=en-US&query={name}&page=1'
        search_response = requests.get(search_url)
        search_results = search_response.json()

        if search_response.status_code == 200 and search_results['results']:
            actor_data = search_results['results'][0]
            actor_id = actor_data['id']
            actor, created = Actor.objects.get_or_create(
                name=name, defaults={'tmdb_id': actor_id})

            # دانلود تصویر بازیگر و ذخیره آن
            if actor_data.get('profile_path'):
                profile_image_url = f'https://image.tmdb.org/t/p/w500{
                    actor_data["profile_path"]}'
                save_actor_image(actor, profile_image_url)

            # دریافت اطلاعات فیلم‌هایی که بازیگر در آن‌ها بازی کرده
            movie_credits_url = f'https://api.themoviedb.org/3/person/{
                actor_id}/movie_credits?api_key={tmdb_api_key}'
            movie_credits_response = requests.get(movie_credits_url)
            movie_credits_results = movie_credits_response.json()

            if movie_credits_response.status_code == 200:
                movies = movie_credits_results.get('cast', [])
                for movie_data in movies:
                    movie, created = Movie.objects.get_or_create(
                        tmdb_id=movie_data['id'],
                        defaults={
                            'title': movie_data['title'],
                            'release_date': movie_data['release_date'],
                        }
                    )
                    if movie_data.get('poster_path'):
                        poster_image_url = f'https://image.tmdb.org/t/p/w500{
                            movie_data["poster_path"]}'
                        save_movie_poster(movie, poster_image_url)
                    if created:
                        actor.movies.add(movie)

            print(
                f"اطلاعات به طور کامل دانلود و ذخیره شده برای بازیگر: {name}")
        else:
            print(f"بازیگر '{name}' پیدا نشد.")


def get_actor_tmdb_id(api_key, name):
    search_url = f'https://api.themoviedb.org/3/search/person?api_key={
        api_key}&query={name}'
    response = requests.get(search_url)
    if response.status_code == 200:
        search_results = response.json().get('results', [])
        if search_results:
            # برگرفتن اولین نتیجه
            actor_id = search_results[0]['id']
            return actor_id
    return None


# @transaction.atomic
# def download_actor_movies(actor_name, tmdb_api_key):
#     actor = get_or_create_actor(tmdb_api_key, actor_name)
#     if not actor:
#         print(f"Actor {actor_name} was not found or could not be created.")
#         return

#     actor_id = actor.tmdb_id
#     credits_url = f'https://api.themoviedb.org/3/person/{
#         actor_id}/movie_credits?api_key={tmdb_api_key}&language=en-US'
#     credits_response = requests.get(credits_url)
#     if credits_response.status_code == 200:
#         credits = credits_response.json()
#         for movie_data in credits['cast']:
#             movie, movie_created = Movie.objects.get_or_create(
#                 title=movie_data['title'],
#                 defaults={
#                     'release_date': movie_data.get('release_date'),
#                     'description': movie_data.get('overview'),
#                     'poster': f'https://image.tmdb.org/t/p/original{movie_data["poster_path"]}' if movie_data.get("poster_path") else None,
#                 }
#             )
#             actor.movies.add(movie)  # این خط باید داخل حلقه باشد
#             if movie_created:
#                 print(f'Movie "{movie.title}" created.')
#             else:
#                 print(f'Movie "{movie.title}" already exists.')
#     else:
#         print(f"Failed to retrieve movie credits for actor {
#               actor_name}. Status Code: {credits_response.status_code}")


# def get_or_create_actor(tmdb_api_key, actor_id):
#     actor_url = f'https://api.themoviedb.org/3/person/{
#         actor_id}?api_key={tmdb_api_key}'
#     response = requests.get(actor_url)

#     if response.status_code == 200:
#         actor_data = response.json()
#         name = actor_data.get('name')
#         actor, created = Actor.objects.get_or_create(name=name)

#         if actor_data.get("profile_path") and not actor.poster:
#             actor_image_url = f'https://image.tmdb.org/t/p/original{
#                 actor_data["profile_path"]}'
#             save_actor_image(actor, actor_image_url)

#         return actor, created
#     else:
#         print(f'Failed to retrieve actor data for TMDB ID {
#             actor_id}. Status Code: {response.status_code}')
#         return None, False


# def get_or_create_director(tmdb_api_key, director_id):
#     director_url = f'https://api.themoviedb.org/3/person/{
#         director_id}?api_key={tmdb_api_key}'
#     response = requests.get(director_url)
#     director_data = response.json()
#     if response.status_code == 200:
#         director, created = Director.objects.get_or_create(
#             full_name=director_data['name'],
#             defaults={
#                 # 'poster' field will be handled below if created is True.
#             }
#         )

#     if created:
#         if director_data.get('profile_path'):
#             poster_url = f'https://image.tmdb.org/t/p/original{
#                 director_data["profile_path"]}'
#             poster_response = requests.get(poster_url)
#             if poster_response.status_code == 200:
#                 director.poster.save(
#                     f'{director_id}_{slugify(director.full_name)}.jpg',
#                     ContentFile(poster_response.content),
#                     save=True
#                 )
#             print(f'Director "{director.full_name}" created.')
#         else:
#             print(f'Director "{director.full_name}" already exists.')

#         return director
#     else:
#         print(f'Could not retrieve director with TMDB ID {director_id}')
#         return None


# def get_or_create_genre(genre_name):
#     genre, created = Genre.objects.get_or_create(name=genre_name)
#     if created:
#         print(f'Genre "{genre.name}" created.')
#     else:
#         print(f'Genre "{genre.name}" already exists.')
#     return genre


# @transaction.atomic
# def get_or_create_movie(tmdb_api_key, movie_id):
#     movie_url = f'https://api.themoviedb.org/3/movie/{
#         movie_id}?api_key={tmdb_api_key}&append_to_response=credits'
#     response = requests.get(movie_url)

#     if response.status_code == 200:
#         movie_data = response.json()

#         imdb_id = movie_data.get('imdb_id')
#         if not imdb_id:
#             # اگر فیلم شناسه IMDb نداشته باشد، نمی‌توانیم آن را ایجاد کنیم.
#             print(f"Movie with TMDB ID {movie_id} does not have an IMDb ID.")
#             return None

#         movie, created = Movie.objects.get_or_create(
#             imdb_id=imdb_id,
#             defaults={
#                 'title': movie_data['title'],
#                 'release_date': movie_data.get('release_date'),
#                 'description': movie_data.get('overview'),
#                 'duration': movie_data.get('runtime'),
#                 'imdb_rating': movie_data.get('vote_average'),
#                 'poster': 'https://image.tmdb.org/t/p/original' + movie_data["poster_path"] if movie_data.get("poster_path") else '',
#             }
#         )

#         if created:
#             if movie_data.get("poster_path"):
#                 poster_url = f'https://image.tmdb.org/t/p/original{
#                     movie_data["poster_path"]}'
#                 save_movie_poster(movie, poster_url)
#             # به‌روزرسانی slug و اضافه کردن ژانرها، بازیگران و کارگردان.
#             movie.slug = slugify(movie_data['title'])
#             # ذخیره تغییرات slug قبل از اضافه کردن روابط many-to-many.
#             movie.save()

#             for genre_name in [genre['name']
#                                for genre in movie_data.get('genres', [])]:
#                 genre, _ = get_or_create_genre(genre_name)
#                 movie.genres.add(genre)

#             director_id = next((crew['id'] for crew in movie_data
#                                 ['credits'].get('crew', [])
#                                 if crew.get('job') == 'Director'), None)
#             if director_id:
#                 director, _ = get_or_create_director(tmdb_api_key, director_id)
#                 movie.director = director
#                 movie.save()  # ذخیره تغییرات director.

#             for cast in movie_data['credits'].get('cast', []):
#                 actor_id = cast['id']
#                 actor, created = get_or_create_actor(tmdb_api_key, actor_id)
#                 if created:
#                     movie.cast.add(actor)

#             print(f'Movie "{movie.title}" created.')
#         else:
#             print(f'Movie "{movie.title}" already exists.')

#         return movie

#     else:
#         print(f"Failed to retrieve movie data for TMDB ID {
#             movie_id}. Status Code: {response.status_code}")
#         return None
