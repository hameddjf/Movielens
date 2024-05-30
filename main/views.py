from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.conf import settings

import requests
from datetime import datetime, timedelta

from .models import Movie, Review
from .utils import save_movie_details

from episode.models import Episode
from category.models import Category
# from cast.models import Actor, Director


def save_movie_view(request, movie_title):
    save_movie_details(movie_title)
    return JsonResponse({'status': 'success', 'message':
                         f"Details for '{movie_title}' have been saved."})


def get_movie_data(imdb_id):
    """
     این تابع با استفاده از
     IMDb ID یک فیلم، اطلاعات آن فیلم را از
     OMDB API دریافت می‌کند.
    """
    params = {
        'i': imdb_id,
        'apikey': settings.OMDB_API_KEY
    }
    response = requests.get(settings.OMDB_API_URL, params=params)
    movie_data = response.json()
    return movie_data

# Create your views here.


class MovieListView(ListView):
    last_month = datetime.today() - timedelta(days=30)
    model = Movie
    template_name = 'main/index.html'
    context_object_name = 'movies'
    paginate_by = 10  # تعداد فیلم‌ها در هر صفحه

    def get_queryset(self):
        today = timezone.now().date()
        genre = self.request.GET.get('genre', None)
        queryset = Movie.objects.annotate(average_rating=Avg(
            'rating__average'), num_views=Count('views'))
        if genre:
            queryset = queryset.filter(genres__id=genre)
        return queryset.filter(
            release_date__lte=today).order_by('-release_date')

    def get_context_data(self, *kwargs):
        context = super().get_context_data(*kwargs)
        today = timezone.now().date()
        movie_list_with_ratings = Movie.objects.annotate(
            average_rating=Avg('imdb_rating')
        )
        past_movies_with_ratings = movie_list_with_ratings.filter(
            release_date__lte=today
        )
        categories = Category.objects.all()
        context['categories'] = categories

        context['categorized_movies'] = []

        seen_movies = set()

        for category in categories:
            movies = {
                'created_at': {'name': 'اخیرا', 'data': Movie.objects.filter(category=category).filter(release_date__lte=today).order_by('-created_at').distinct()[:12]},
                'release_date': {'name': 'جدیدترین', 'data': Movie.objects.filter(category=category).filter(release_date__lte=today).order_by('-release_date').distinct()[:12]},
                'popular_movies': {'name': 'محبوب', 'data': Movie.objects.filter(category=category).filter(release_date__lte=today).order_by('-views').distinct()[:12]},
                'coming_soon_movies': {'name': 'بزودی', 'data': Movie.objects.filter(category=category).filter(release_date__gt=today).order_by('release_date').distinct()[:10]},
                'top_rated': {'name': 'بیشترین امتیاز', 'data': past_movies_with_ratings.filter(category=category).exclude(average_rating__isnull=True).order_by('-average_rating').distinct()[:10]},
                'top_rated_imdb': {'name': 'IMDb', 'data': past_movies_with_ratings.filter(category=category).exclude(imdb_rating__isnull=True).order_by('-imdb_rating').distinct()[:12]}
            }

            context['categorized_movies'].append(
                {'category': category, 'movies': movies})

        return context

    # def get_context_data(self, **kwargs):
    #     context = super(MovieListView, self).get_context_data(**kwargs)

    #     # دریافت تاریخ امروز
    #     today = timezone.now().date()

    #     # استخراج دسته‌بندی‌ها
    #     categories = Category.objects.all()
    #     context['categories'] = categories

    #     # اضافه کردن میانگین امتیاز به تمام فیلم‌ها
    #     movie_list_with_ratings = Movie.objects.annotate(
    #         average_rating=Avg('rating__average')
    #     )

    #     # فیلتر کردن فیلم‌های با تاریخ انتشار در گذشته
    #     past_movies_with_ratings = movie_list_with_ratings.filter(
    #         release_date__lte=today
    #     )

    #     # اضافه کردن فیلم‌های بر اساس تاریخ انتشار
    #     context['created_at'] = past_movies_with_ratings.order_by(
    #         '-created_at')[:12]

    #     context['release_date'] = past_movies_with_ratings.order_by(
    #         '-release_date')[:12]

    #     context['popular_movies'] = past_movies_with_ratings.order_by(
    #         '-views')[:12]

    #     # مرتب سازی بر اساس امتیاز کاربران، با محدودیت برای فیلم‌هایی که امتیاز دارند
    #     top_rated_movies = past_movies_with_ratings.exclude(
    #         average_rating__isnull=True).order_by('-average_rating')[:10]
    #     context['top_rated_movies'] = top_rated_movies

    #     # فیلتر کردن فیلم‌های آینده و مرتب سازی بر اساس تاریخ انتشار
    #     context['coming_soon_movies'] = movie_list_with_ratings.filter(
    #         release_date__gt=today
    #     ).order_by('release_date')[:10]

    #     # مرتب سازی بر اساس امتیاز کاربران برای نمایش در صفحه جزئیات
    #     top_rated_movies_imdb = past_movies_with_ratings.exclude(
    #         imdb_rating__isnull=True).order_by('-imdb_rating')[:12]
    #     top_rated_movies_data = [
    #         (movie, {'rating': movie.imdb_rating})
    #         for movie in top_rated_movies_imdb]
    #     context['top_rated_movies_data'] = top_rated_movies_data

    #     imdb_ratings_dict = {movie.id: movie.imdb_rating for movie in past_movies_with_ratings.exclude(
    #         imdb_rating__isnull=True)}
    #     context['imdb_ratings_dict'] = imdb_ratings_dict

    #     return context

# نمایش جزئیات یک فیلم:


# class AverageRatingView(View):
#     def get(self, request):
#         rating = AbstractBaseRating()
#         rating.calculate()
#         return HttpResponse("Average rating calculated.")


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'main/moviesingle.html'
    context_object_name = 'movie'
    slug_field = 'slug'  # فیلد slug که به نام 'slug' تعریف شده
    slug_url_kwarg = 'slug'  # نام کلیدی که در URL برای slug انتظار می‌رود

    def get_object(self, queryset=None):
        """Override get_object to handle custom logic."""
        obj = super().get_object(queryset=queryset)  # Get the base object

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = context['movie']

        imdb_id = self.kwargs.get('imdb_id')
        movie_data = get_movie_data(imdb_id)

        context['movie_data'] = movie_data

        context['reviews'] = Review.objects.get_approved().filter(movie=movie)

        return context

# نمایش لیست بررسی‌های تایید شده برای یک فیلم


class ApprovedReviewListView(ListView):
    model = Review
    template_name = 'reviews/approved_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        movie_id = self.kwargs.get('movie_id')
        movie = get_object_or_404(Movie, pk=movie_id)
        return Review.objects.get_approved().filter(movie=movie)

# اضافه کردن یک بررسی جدید برای فیلم:


class AddReviewView(View):
    def post(self, request, *args, **kwargs):
        movie_id = self.kwargs.get('movie_id')
        movie = get_object_or_404(Movie, pk=movie_id)
        user = request.user
        content = request.POST.get('content')
        rating = request.POST.get('rating')

        Review.objects.create(movie=movie, user=user,
                              content=content, rating=rating)

        return HttpResponseRedirect(reverse('movie_detail',
                                            kwargs={'slug': movie.slug}))


class EpisodeListView(ListView):
    model = Episode
    template_name = 'episodes/episode_list.html'
    context_object_name = 'episodes'

    def get_queryset(self):
        """
        فیلتر کردن قسمت‌ها بر اساس سریال مربوطه که از طریق
        slug در URL دریافت شده است.
        """
        movie_slug = self.kwargs.get('movie_slug')
        return Episode.objects.filter(movie__slug=movie_slug)
