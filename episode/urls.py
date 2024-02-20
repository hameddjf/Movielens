from django.urls import path
from .views import EpisodeDetailView

app_name = 'episode'
urlpatterns = [
    path('episodes/<int:pk>/', EpisodeDetailView.as_view(), name='episode-detail'),
]