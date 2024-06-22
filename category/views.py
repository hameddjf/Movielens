from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Min, Max, Q
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseRedirect

from datetime import datetime

from .models import Category

from main.models import Movie
import math


class CategoryListView(ListView):
    template_name = 'main/moviegrid.html'
    context_object_name = 'categorized_movies'
    paginate_by = 12

    def get_queryset(self):
        slug = self.kwargs.get('slug', None)

        if slug:
            category = get_object_or_404(Category, slug=slug)
            queryset = Movie.objects.filter(category=category)
        else:
            queryset = Movie.objects.all()

        queryset = self._apply_filters(queryset)
        queryset = self._apply_ordering(queryset)
        return queryset.annotate(average_rating=Avg('imdb_rating'))

    def _apply_filters(self, queryset):
        # query_params = self.request.GET.copy()

        # if 'movie_name' in query_params:
        # movie_name = query_params.get('movie_name')
        # queryset = queryset.filter(title__icontains=movie_name)

        if 'movie_name' in self.request.GET:
            movie_name = self.request.GET.get('movie_name')
            queryset = queryset.filter(title__icontains=movie_name)

        if 'genre' in self.request.GET:
            genre_name = self.request.GET.get('genre')
            queryset = queryset.filter(genres__name__icontains=genre_name)

        if 'release_year_from' in self.request.GET and 'release_year_to' in self.request.GET:
            from_year = self.request.GET.get('release_year_from')
            to_year = self.request.GET.get('release_year_to')
            if from_year.isdigit() and to_year.isdigit():
                start_date = datetime(int(from_year), 1, 1)
                end_date = datetime(int(to_year), 12, 31)
                queryset = queryset.filter(
                    release_date__range=(start_date, end_date))

        if 'rating_range' in self.request.GET:
            rating_range = self.request.GET.get('rating_range')
            if rating_range.strip():
                min_filter, max_filter = map(float, rating_range.split('-'))
                queryset = queryset.filter(
                    imdb_rating__range=(min_filter, max_filter))

        return queryset

    def _apply_ordering(self, queryset):
        filter_order = self.request.GET.get('filter_by', '_').split('_')
        filter_by = filter_order[0]
        order_by = 'desc' if len(
            filter_order) > 1 and filter_order[1] == 'desc' else 'asc'

        if filter_by == 'popularity':
            order = '-views' if order_by == 'desc' else 'views'
        elif filter_by == 'rating':
            order = '-imdb_rating' if order_by == 'desc' else 'imdb_rating'
        elif filter_by == 'date':
            order = '-release_date' if order_by == 'desc' else 'release_date'
        else:
            order = '-release_date'
        return queryset.order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['genres'] = Movie.objects.values_list(
            'genres__name', flat=True).distinct()
        context['rating_ranges'] = self.get_rating_ranges()
        context['years_range'] = self.get_years_range()

        context['query_params'] = self.request.GET.urlencode()
        return context

    def get_rating_ranges(self):
        min_rating = Movie.objects.aggregate(Min('imdb_rating'))[
            'imdb_rating__min'] or 0
        max_rating = Movie.objects.aggregate(Max('imdb_rating'))[
            'imdb_rating__max'] or 10
        min_rounded_rating = math.ceil(min_rating)
        max_rounded_rating = math.ceil(max_rating)

        rating_ranges = []
        for i in range(min_rounded_rating, max_rounded_rating):
            rating_ranges.append((i, i+1))

        return rating_ranges

    def get_years_range(self):
        min_release_year = Movie.objects.aggregate(Min('release_date'))[
            'release_date__min'].year if Movie.objects.aggregate(Min('release_date'))['release_date__min'] else None
        max_release_year = Movie.objects.aggregate(Max('release_date'))[
            'release_date__max'].year if Movie.objects.aggregate(Max('release_date'))['release_date__max'] else None
        return list(range(min_release_year, max_release_year + 1)) if min_release_year and max_release_year else []
