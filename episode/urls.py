from django.urls import path
from .views import EpisodeDetailView

urlpatterns = [
    path('episodes/<int:pk>/', EpisodeDetailView.as_view(), name='episode-detail'),
]