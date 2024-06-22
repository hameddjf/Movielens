from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from .models import Actor, Director

from itertools import chain


class CelebrityListView(ListView):
    template_name = 'main/celebrity.html'
    context_object_name = 'celebrities'
    paginate_by = 12

    def get_queryset(self):
        actors_with_photo = Actor.objects.exclude(
            poster__isnull=True)
        directors_with_photo = Director.objects.exclude(
            poster__isnull=True)

        filter_order = self.request.GET.get('filter_by', 'name_asc')

        if filter_order == 'name_asc':
            actors_with_photo = actors_with_photo.order_by('name')
            directors_with_photo = directors_with_photo.order_by('full_name')
        elif filter_order == 'name_desc':
            actors_with_photo = actors_with_photo.order_by('-name')
            directors_with_photo = directors_with_photo.order_by('-full_name')
        elif filter_order == 'rating_asc':
            actors_with_photo = actors_with_photo.order_by('rating')
            directors_with_photo = directors_with_photo.order_by('rating')
        elif filter_order == 'rating_desc':
            actors_with_photo = actors_with_photo.order_by('-rating')
            directors_with_photo = directors_with_photo.order_by('-rating')
        elif filter_order == 'date_asc':
            actors_with_photo = actors_with_photo.order_by('release_date')
            directors_with_photo = directors_with_photo.order_by(
                'release_date')
        elif filter_order == 'date_desc':
            actors_with_photo = actors_with_photo.order_by('-release_date')
            directors_with_photo = directors_with_photo.order_by(
                '-release_date')
        else:
            actors_with_photo = actors_with_photo.order_by('-name')
            directors_with_photo = directors_with_photo.order_by('-full_name')

        combined_list = list(chain(actors_with_photo, directors_with_photo))

        return combined_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(*kwargs)

        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['query_params'] = query_params.urlencode()

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
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']

        # اعمال فیلتر روی تمامی صفحات
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
            queryset = actors_query.order_by('name')
        elif celebrity_type == 'director':
            queryset = directors_query.order_by('full_name')
        else:
            combined_list = list(chain(actors_query, directors_query))
            queryset = combined_list

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
