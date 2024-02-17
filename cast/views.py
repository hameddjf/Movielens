from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Actor, Director

class ActorListView(ListView):
    model = Actor
    template_name = 'actors/actor_list.html'
    context_object_name = 'actors'

class ActorDetailView(DetailView):
    model = Actor
    template_name = 'actors/actor_detail.html'
    context_object_name = 'actor'

class DirectorListView(ListView):
    model = Director
    template_name = 'directors/director_list.html'
    context_object_name = 'directors'

class DirectorDetailView(DetailView):
    model = Director
    template_name = 'directors/director_detail.html'
    context_object_name = 'director'