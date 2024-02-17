from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Episode, Series

class EpisodeDetailView(View):
    def get(self, request, *args, **kwargs):
        episode_id = kwargs.get('pk')
        try:
            episode = Episode.objects.get(pk=episode_id)
            qualities = episode.qualities.all()
            data = {
                'id': episode.id,
                'title': episode.title,
                'movie_type': 'سریال' if isinstance(episode.movie, Series) else 'فیلم',
                'season': episode.season,
                'qualities': list(qualities.values('quality', 'file'))
            }
            return JsonResponse(data)
        except Episode.DoesNotExist:
            return JsonResponse({'error': 'Episode not found'}, status=404)