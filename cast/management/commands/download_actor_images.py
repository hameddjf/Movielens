import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from cast.models import Actor, Director
from main.models import Movie, Genre
import datetime
from io import BytesIO
from PIL import Image
from category.models import Category

tmdb_api_key = settings.TMDB_API_KEY


class Command(BaseCommand):
    help = 'تصاویر بازیگران و اطلاعات فیلم‌هایشان را از TMDb دانلود و ذخیره کنید'

    def add_arguments(self, parser):
        parser.add_argument('actor_name', nargs='+', type=str,
                            help='لیست اسامی بازیگران برای دانلود تصاویر و دریافت اطلاعات فیلم')

    def get_or_create_actor(self, actor_name, tmdb_id):
        actor, created = Actor.objects.get_or_create(
            name=actor_name,
            defaults={'tmdb_id': tmdb_id,
                      'poster': f'actors/{slugify(actor_name)}.jpg'}
        )

        if created:
            print(f'بازیگر جدید با نام "\
                  {actor_name}" و TMDB ID {tmdb_id} ایجاد شد.')
        else:
            updated = False
            if actor.tmdb_id != tmdb_id:
                actor.tmdb_id = tmdb_id
                updated = True
                print(f'TMDB ID برای بازیگر "{actor_name}" به‌روزرسانی شد.')

            if not actor.poster:
                actor.poster = f'actors/{slugify(actor_name)}.jpg'
                updated = True
                print(f'عکس برای بازیگر "{actor_name}" اضافه شد.')

            if updated:
                actor.save()
            else:
                print(f'بازیگر "{actor_name}" همراه با عکس قبلاً موجود است.')

        return actor

    def get_or_create_director(self, director_id, director_name):
        tmdb_api_key = settings.TMDB_API_KEY
        image_base_url = "https://image.tmdb.org/t/p/w500"

        # Fetch director details from TMDB API
        director_details_url = f"https://api.themoviedb.org/3/person/{
            director_id}?api_key={tmdb_api_key}"

        try:
            response = requests.get(director_details_url)
            response.raise_for_status()
            director_data = response.json()
            director_profile_path = director_data.get('profile_path')

            if director_profile_path:
                director_image_url = f"{image_base_url}{director_profile_path}"
            else:
                director_image_url = None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching director details for '{
                  director_name}': {e}")
            director_image_url = None

        # Get or create the director object with the fetched or default data
        director, created = Director.objects.get_or_create(
            tmdb_id=director_id,
            defaults={
                'full_name': director_name,
                'poster': director_image_url  # Store the image URL directly
            }
        )

        return director, created

    def save_actor_image(self, actor_name):
        tmdb_api_key = settings.TMDB_API_KEY
        search_url = f'https://api.themoviedb.org/3/search/person?api_key={
            tmdb_api_key}&query={actor_name}'
        self.stdout.write(f"Fetching actor information for '{
                          actor_name}' from TMDB...")
        search_response = requests.get(search_url)

        if search_response.status_code == 200:
            search_results = search_response.json().get('results', [])
            if search_results:
                actor_data = search_results[0]
                tmdb_id = actor_data.get('id')
                self.stdout.write(f"TMDB ID for '{actor_name}' is: {tmdb_id}")
                profile_path = actor_data.get('profile_path')
                if profile_path:
                    image_url = f'https://image.tmdb.org/t/p/w500{
                        profile_path}'
                    actor = self.get_or_create_actor(actor_name, tmdb_id)
                    actor.poster = image_url  # Update 'poster' field with the image URL
                    actor.save()
                    self.stdout.write(
                        f'Image URL {image_url} saved for actor {actor_name}.')
                else:
                    self.stdout.write(
                        f'No image found for actor "{actor_name}".')
        else:
            self.stdout.write(
                f'Failed to fetch actor information for "{actor_name}".')

    def get_actors_for_movie(self, tmdb_movie_id):
        tmdb_api_key = settings.TMDB_API_KEY
        movie_cast_url = f'https://api.themoviedb.org/3/movie/{
            tmdb_movie_id}/credits?api_key={tmdb_api_key}'
        print(f"movie_cast_url:  {movie_cast_url}")

        movie_cast_response = requests.get(movie_cast_url)
        actors_list = []
        print(f"actors_list:  {actors_list}")

        if movie_cast_response.status_code == 200:
            print(f"movie_cast_response:  {movie_cast_response}")

            movie_cast_results = movie_cast_response.json()
            cast_members = movie_cast_results.get('cast', [])

            for actor_data in cast_members:
                actor_tmdb_id = actor_data['id']
                actor_name = actor_data['name']
                actor_profile_path = actor_data.get('profile_path')
                actor_image_url = f"https://image.tmdb.org/t/p/w500{
                    actor_profile_path}" if actor_profile_path else None

                content_file, file_name = self.download_image(
                    actor_image_url, actor_name)

                actors_list.append({
                    'tmdb_id': actor_tmdb_id,
                    'name': actor_name,
                    'image_url': actor_image_url,
                    'content_file': content_file,
                    'file_name': file_name
                })

        return actors_list

    def download_image(self, image_url, actor_name):
        if image_url:
            print(f"image_url:  {image_url}")

            response = requests.get(image_url)
            print(f"response:  {response}")

            if response.status_code == 200:
                # Create a PIL Image object from the downloaded data
                image = Image.open(BytesIO(response.content))

                # Save the image to a BytesIO object
                buffer = BytesIO()
                image.save(buffer, format='JPEG')

                # Create a Django ContentFile object from the BytesIO buffer
                content_file = ContentFile(buffer.getvalue())

                # Define the file name
                file_name = f"{slugify(actor_name)}.jpg"

                return content_file, file_name
            else:
                print(f"Failed to download image for {actor_name}")

        return None, None

    def save_movie_poster(self, movie, image_url):
        """به‌روزرسانی شی movie با URL تصویر."""

        if image_url:
            # ذخیره سازی URL تصویر در فیلد 'poster' شی movie
            movie.poster = image_url
            movie.save()
            print(f'Image URL {image_url} saved for movie {movie.title}.')
        else:
            print(f'No image URL provided for movie {movie.title}.')

    def get_category(self, media_type):
        """
        Get or create a Category instance based on the given media_type.
        """
        category_title = {
            'movie': 'فیلم',
            'tv': 'سریال',
            'animation': 'انیمیشن',
            # Add more media types if needed
        }.get(media_type.lower(), 'سایر')

        category, created = Category.objects.get_or_create(
            title=category_title,
            defaults={'slug': slugify(category_title)}
        )
        return category

    def get_movies_for_actor(self, actor):
        tmdb_api_key = settings.TMDB_API_KEY
        movie_credits_url = f"https://api.themoviedb.org/3/person/{
            actor.tmdb_id}/movie_credits?api_key={tmdb_api_key}"
        print(f"Fetching movies for actor with TMDB ID: {actor.tmdb_id}")
        movie_credits_response = requests.get(movie_credits_url)
        movies = []

        if movie_credits_response.status_code == 200:
            movie_credits_results = movie_credits_response.json()
            cast_movies = movie_credits_results.get('cast', [])

            for movie_data in cast_movies:
                tmdb_movie_id = movie_data['id']
                print(f'movie_id : {tmdb_movie_id}')
                movie_title = movie_data['title']
                release_date = movie_data.get('release_date')
                if release_date:
                    release_date = datetime.datetime.strptime(
                        release_date, '%Y-%m-%d').date()
                # poster movie
                poster_url = f"https://image.tmdb.org/t/p/w500{
                    movie_data['poster_path']}"

                # Fetch detailed movie information including the director
                detailed_movie_response = requests.get(f'https://api.themoviedb.org/3/movie/{
                                                       tmdb_movie_id}?api_key={tmdb_api_key}&append_to_response=credits')
                print(f'detailed_movie_response : {tmdb_movie_id}')
                duration = None
                director_id = None
                media_type = None

                if detailed_movie_response.status_code == 200:
                    detailed_movie_data = detailed_movie_response.json()
                    duration = detailed_movie_data.get('runtime', None)
                    media_type = detailed_movie_data.get('media_type', 'movie')
                    media_type = self.detect_media_type(movie_data)

                    # Extract director information
                    credits = detailed_movie_data.get('credits', {})
                    crew = credits.get('crew', [])
                    director = next(
                        (person for person in crew if person.get('job') == 'Director'), None)

                    if director:
                        director_name = director.get('name')
                        director_id = director.get('id')
                        print(f"Director found: {director_name}")
                        # Use get_or_create_director to retrieve or create director
                        director_object, created = self.get_or_create_director(
                            director_id, director_name)
                        if director_object is not None:
                            director_id = director_object.id
                            # Now you have the director, you can create/update the movie in the database
                            # Your code to create/update movie goes here
                        else:
                            print(f"Failed to create or find director with TMDB ID {
                                  director_id}")
                            continue  # Skip this movie if director creation failed
                    else:
                        print("No director found in the API response")
                        continue  # Skip this movie if no director is found
                else:
                    print(f"Failed to fetch details for movie ID {
                          tmdb_movie_id}. Status code: {detailed_movie_response.status_code}")
                    continue  # Skip this movie if detailed fetch failed

                # genres
                genres_data = detailed_movie_data.get('genres', [])
                if not genres_data:
                    print("No genres found for the movie.")
                    # اقدامات مورد نیاز شما در صورت عدم وجود ژانرها
                else:
                    for genre_data in genres_data:
                        genre_name = genre_data['name']
                        print(f'genre_data : {
                              genre_data} , genre_name {genre_name}')
                        # اقدامات مورد نیاز شما با هر ژانر

                # ایجاد یا به‌روزرسانی رکورد فیلم در دیتابیس
                movie, created = Movie.objects.get_or_create(
                    type=self.get_category(media_type),
                    tmdb_id=tmdb_movie_id,
                    defaults={
                        'title': movie_title,
                        'release_date': release_date,
                        'imdb_rating': movie_data.get('vote_average', None),
                        'duration': duration,
                        'description': movie_data.get('overview', ''),
                        'poster': poster_url,  # Update 'poster' field
                        'director_id': director_id,
                        'type': self.get_category(media_type)
                    }
                )
                self.save_movie_poster(movie, poster_url)

                if created:
                    print(f"Movie '{movie_title}' created with director: {
                          director_name}")
                else:
                    print(f"Movie '{movie_title}' updated with director: {
                          director_name}")

                # اضافه کردن فیلم به مدل Director
                if created and director_object:
                    director_object.movies.add(movie)
                    director_object.save()

                # Fetch Genres in Movie
                genres = []
                for genre_data in genres_data:
                    genre_id = genre_data['id']
                    genre_name = genre_data['name']
                    try:
                        genre = Genre.objects.get(name=genre_name)
                    except Genre.DoesNotExist:
                        genre = Genre.objects.create(
                            id=genre_id, name=genre_name)
                    genres.append(genre)

                movie.genres.set(genres)

                # Fetch actors Movie & Actor models
                actors_list = self.get_actors_for_movie(tmdb_movie_id)
                for actor_info in actors_list:
                    tmdb_id = actor_info['tmdb_id']
                    name = actor_info['name']
                    image_url = actor_info['image_url']

                    actor_obj, actor_created = Actor.objects.get_or_create(
                        tmdb_id=tmdb_id,
                        defaults={
                            'name': name,
                            'poster': image_url
                        }
                    )

                    movie.actor.add(actor_obj)
                    movie.actors.add(actor_obj)

                movies.append(movie)
        else:
            print(f"Failed to fetch movies for actor. Status code: {
                  movie_credits_response.status_code}")

        return movies

    def detect_media_type(self, movie_data):
        # اینجا منطق برای تشخیص نوع رسانه بر اساس داده‌های موجود در movie_data اضافه می‌شود
        # به عنوان مثال:
        keywords = movie_data.get('overview', '').lower()
        if 'anime' in keywords or 'animation' in keywords:
            return 'animation'
        elif 'series' in keywords or 'tv' in keywords:
            return 'tv'
        else:
            return 'movie'

    def handle(self, *args, **options):
        actor_names = options['actor_name']
        for actor_name in actor_names:
            try:
                actor, created = Actor.objects.get_or_create(name=actor_name)
                if not created:
                    print(
                        f"Actor '{actor.name}' already exists. Updating movies and image.")

                # فرض می‌کنیم که `get_movies_for_actor` یک لیست از فیلم‌ها را برمی‌گرداند
                movies = self.get_movies_for_actor(actor)
                self.save_actor_image(actor_name)

                directors = set()  # برای نگهداری اسامی یکتای کارگردان‌ها و جلوگیری از تکرار
                for movie in movies:
                    director_id, director_name = self.get_or_create_director(
                        movie['id'])
                    if director_id and director_name:
                        # اضافه کردن نام کارگردان به مجموعه اگر قبلا اضافه نشده باشد
                        if director_name not in directors:
                            directors.add(director_name)
                            self.save_director_image(director_name)

                        director, created = self.get_or_create_director(
                            director_id, director_name)
                        if not created:
                            print(f"Director '{
                                  director.name}' already exists. Updating information.")

                print(f"Found {len(movies)} movies for actor '{actor_name}'.")
            except Exception as e:
                print(f"Error processing actor '{actor_name}': {e}")
