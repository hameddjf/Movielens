from django.urls import path
from .views import CelebrityListView, ActorDetailView, DirectorDetailView

app_name = 'cast'
urlpatterns = [
    path('celebrity/', CelebrityListView.as_view(), name='celebrity_list'),
    path('actors/<int:pk>/', ActorDetailView.as_view(), name='actor_detail'),
    path('directors/<int:pk>/', DirectorDetailView.as_view(),
         name='director_detail'),
]
