from django.shortcuts import render
from django.template.loader import render_to_string


from .models import Category

from main.models import Movie


def category_list(request):
    categories = Category.objects.all()

    return render(request, 'main/index.html', {'categories': categories})
