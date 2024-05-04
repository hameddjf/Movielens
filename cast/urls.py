from django.urls import path
from . import views

app_name = 'cast'
urlpatterns = [
    path('celebrity/', views.CelebrityListView.as_view(),
         name='celebrity_list'),
    path('actors/<int:pk>/', views.ActorDetailView.as_view(),
         name='actor_detail'),
    path('directors/<int:pk>/', views.DirectorDetailView.as_view(),
         name='director_detail'),
    path('search/', views.CelebritySearchView.as_view(),
         name='search_celebrity'),
]
