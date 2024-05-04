from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator

from .models import Actor, Director

from itertools import chain


class CelebrityListView(ListView):
    template_name = 'main/celebrity.html'
    context_object_name = 'celebrities'
    paginate_by = 12

    def get_queryset(self):
        # بازیگرانی که عکس دارند
        actors_with_photo = Actor.objects.exclude(
            poster__isnull=True).order_by('name')
        directors_with_photo = Director.objects.exclude(
            poster__isnull=True).order_by('full_name')
        # کارگردان‌هایی که عکس دارند
        # ترکیب دو لیست
        combined_list = list(chain(actors_with_photo, directors_with_photo))
        return combined_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CelebritySearchView(ListView):
    template_name = 'main/celebrity.html'
    context_object_name = 'celebrities'
    paginate_by = 12

    def get_queryset(self):
        celebrity_name = self.request.GET.get('celebrity_name', '')
        celebrity_letter = self.request.GET.get('celebrity_letter', '')
        celebrity_type = self.request.GET.get('celebrity_type', '')

        actors_query = Actor.objects.exclude(poster__isnull=True)
        directors_query = Director.objects.exclude(poster__isnull=True)

        if celebrity_name:
            actors_query = actors_query.filter(name__icontains=celebrity_name)
            directors_query = directors_query.filter(
                full_name__icontains=celebrity_name)

        if celebrity_letter:
            actors_query = actors_query.filter(
                name__istartswith=celebrity_letter)
            directors_query = directors_query.filter(
                full_name__istartswith=celebrity_letter)

        if celebrity_type == 'actor':
            return actors_query.order_by('name')
        elif celebrity_type == 'director':
            return directors_query.order_by('full_name')
        else:
            combined_list = list(chain(actors_query, directors_query))
            return combined_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ایجاد یک کوئری استرینگ جدید با پارامترهای جستجو
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = query_params.urlencode()

        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        celebrities_page = paginator.get_page(page)
        context['celebrities'] = celebrities_page
        return context


class ActorDetailView(DetailView):
    model = Actor
    template_name = 'actors/actor_detail.html'
    context_object_name = 'actor'


class DirectorDetailView(DetailView):
    model = Director
    template_name = 'directors/director_detail.html'
    context_object_name = 'director'
