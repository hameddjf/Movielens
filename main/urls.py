from django.contrib import admin
from django.urls import path 
from .views import MovieListView , MovieDetailView , AverageRatingView , get_movie_data

urlpatterns = [
    path("", MovieListView.as_view() , name = 'home'),
    path('movie/<slug:slug>/', MovieDetailView.as_view(), name='movie-detail'),  # اصلاح 'addres' به 'address'
    path('calculate-rating/', AverageRatingView.as_view(), name='calculate-rating'),

    path('movies/<str:imdb_id>/', MovieDetailView.as_view(), name='movie-detail'),

    path('series/<slug:slug>/', MovieDetailView.as_view(), name='series-detail'),
] 
