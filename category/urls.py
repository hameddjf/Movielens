from django.urls import path
from .views import category_list

urlpatterns = [
    path('categories/', category_list, name='category_list'),
]