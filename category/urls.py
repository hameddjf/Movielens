from django.urls import path
from .views import CategoryListView

app_name = 'category'
urlpatterns = [
    path('<slug:slug>/', CategoryListView.as_view(), name='category_list'),
]
