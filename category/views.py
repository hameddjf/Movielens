from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Min, Max, Q

from datetime import datetime

from .models import Category

from main.models import Movie


def category_list(request, slug=None):
    filter_order = request.GET.get('filter_by', '_').split('_')

    filter_by = filter_order[0]
    order_by = 'desc' if len(
        filter_order) > 1 and filter_order[1] == 'desc' else 'asc'

    if slug:
        category = get_object_or_404(Category, slug=slug)
        movies = Movie.objects.filter(
            category=category
        ).annotate(average_rating=Avg('imdb_rating'))

        if 'movie_name' in request.GET:
            movie_name = request.GET.get('movie_name')
            movies = movies.filter(title__icontains=movie_name)

        if filter_by == 'popularity':
            order = '-views' if order_by == 'desc' else 'views'
            movies = movies.order_by(order)
        elif filter_by == 'rating':
            order = '-average_rating' if order_by == 'desc' else 'average_rating'
            movies = movies.order_by(order)
        elif filter_by == 'date':
            order = '-release_date' if order_by == 'desc' else 'release_date'
            movies = movies.order_by(order)

        # genre
        if 'genre' in request.GET:
            genre_name = request.GET.get('genre')
            movies = movies.filter(genres__name__icontains=genre_name)

        genres = movies.values_list('genres__name', flat=True).distinct()

        # release_year
        min_release_year = movies.aggregate(Min('release_date'))['release_date__min'].year if movies.aggregate(
            Min('release_date'))['release_date__min'] else None
        max_release_year = movies.aggregate(Max('release_date'))['release_date__max'].year if movies.aggregate(
            Max('release_date'))['release_date__max'] else None

        if 'release_year_from' in request.GET and 'release_year_to' in request.GET:
            from_year = request.GET.get('release_year_from')
            to_year = request.GET.get('release_year_to')
            if from_year.isdigit() and to_year.isdigit():
                start_date = datetime(int(from_year), 1, 1)
                end_date = datetime(int(to_year), 12, 31)
                movies = movies.filter(
                    release_date__range=(start_date, end_date))

        years_range = list(range(min_release_year, max_release_year + 1)
                           ) if min_release_year and max_release_year else []

        # rating
        min_rating = movies.aggregate(Min('imdb_rating'))[
            'imdb_rating__min'] or 0
        max_rating = movies.aggregate(Max('imdb_rating'))[
            'imdb_rating__max'] or 10
        min_filter = 0
        max_filter = 10
        if 'rating_range' in request.GET:
            rating_range = request.GET.get('rating_range')
            if rating_range.strip():
                min_filter, max_filter = map(float, rating_range.split('-'))

            movies = movies.filter(
                imdb_rating__gte=min_filter, imdb_rating__lte=max_filter)  # تغییر از "<" به "<="

        rating_ranges = [(round(min_rating + i, 1), round(min_rating + i + 1, 1))
                         for i in range(int(max_rating - min_rating))]

        # -----

        movie_count = movies.count()
        return render(request, 'main/moviegrid.html', {
            'categorized_movies': [{
                'category': category, 'movies': movies,
                'movie_count': movie_count,
                'filter_by': filter_by,
                'order_by': order_by,
            }],
            'genres': genres,
            'rating_ranges': rating_ranges,
            'years_range': years_range,

        })
    else:
        categories = Category.objects.all()
        categorized_movies = []
        for category in categories:
            movie_list_with_ratings = Movie.objects.filter(
                category=category).annotate(average_rating=Avg('imdb_rating'))
            categorized_movies.append(
                {'category': category, 'movies': movie_list_with_ratings,
                 'filter_by': filter_by, 'order_by': order_by})
        return render(request, 'main/moviegrid.html',
                      {'categorized_movies': categorized_movies})
