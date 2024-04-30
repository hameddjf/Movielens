from django.views.generic import ListView, DetailView

from .models import Actor, Director


class CelebrityListView(ListView):
    model = Actor
    template_name = 'main/celebrities/celebrity_list.html'
    context_object_name = 'celebrities'
    ordering = ['name']  # Default ordering to name ascending

    def get_queryset(self, context=None):
        queryset = super().get_queryset()
        filter_by = self.request.GET.get('filter_by', 'name')
        order_by = self.request.GET.get('order_by', 'asc')

        if filter_by == 'name':
            if order_by == 'desc':
                queryset = queryset.order_by('-name')
            else:
                queryset = queryset.order_by('name')
        elif filter_by == 'rating':
            if order_by == 'desc':
                queryset = queryset.order_by('-rating')
            else:
                queryset = queryset.order_by('rating')
        elif filter_by == 'date':
            if order_by == 'desc':
                queryset = queryset.order_by('-created')
            else:
                queryset = queryset.order_by('created')

        if context is not None:
            context['actors'] = queryset
            context['directors'] = Director.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_by'] = self.request.GET.get('filter_by', 'name')
        context['order_by'] = self.request.GET.get('order_by', 'asc')
        return context


class ActorDetailView(DetailView):
    model = Actor
    template_name = 'actors/actor_detail.html'
    context_object_name = 'actor'


class DirectorDetailView(DetailView):
    model = Director
    template_name = 'directors/director_detail.html'
    context_object_name = 'director'
