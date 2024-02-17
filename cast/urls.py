from django.urls import path
from .views import ActorListView, ActorDetailView, DirectorListView, DirectorDetailView

urlpatterns = [
    path('actors/', ActorListView.as_view(), name='actor_list'),
    path('actors/<int:pk>/', ActorDetailView.as_view(), name='actor_detail'),
    path('directors/', DirectorListView.as_view(), name='director_list'),
    path('directors/<int:pk>/', DirectorDetailView.as_view(), name='director_detail'),
]