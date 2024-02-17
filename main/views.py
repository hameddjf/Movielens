from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q , Avg
from django.conf import settings
import requests

from datetime import datetime , timedelta

from .models import Movie, Review, Genre
from .utils import save_movie_details  # اطمینان حاصل کنید که مسیر صحیح است
from episode.models import Episode
from cast.models import Actor , Director

def save_movie_view(request, movie_title):
    save_movie_details(movie_title)
    return JsonResponse({'status': 'success', 'message': f"Details for '{movie_title}' have been saved."})

def get_movie_data(imdb_id):
    """
     این تابع با استفاده از IMDb ID یک فیلم، اطلاعات آن فیلم را از OMDB API دریافت می‌کند.
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

    # def get_object(self):
    #     # میاد هرچی ک مال اسلاگه رو میگیره = هرمقداری اسلاگ داشت رو میگیره   تعریف اسلاگ
    #     slug = self.kwargs.get('slug')
    #     # اینجا تعیین کردیم که از مدل .. اسلاگ برابر با اسلاگه
    #     article = get_object_or_404(Movie, slug=slug)
    #     ip_address = self.request.META['ip_address']
    #     if ip_address not in article.rating.all():
    #         article.rating.add(ip_address)
    #     return article

    def get_queryset(self):
        today = timezone.now().date()
        genre = self.request.GET.get('genre', None)
        queryset = Movie.objects.annotate(average_rating=Avg('rating__average'), num_views=Count('views'))
        if genre:
            queryset = queryset.filter(genres__id=genre)
        return queryset.filter(release_date__lte=today).order_by('-release_date')



    def get_context_data(self, **kwargs):
        context = super(MovieListView, self).get_context_data(**kwargs)

        #دریافت تاریخ امروز
        today = timezone.now().date()

           # اضافه کردن میانگین امتیاز به تمام فیلم‌ها
        movie_list_with_ratings = Movie.objects.annotate(
                    average_rating=Avg('rating__average')  # فرض بر این است که فیلد rating به AbstractBaseRating ارتباط دارد
                )

        # فیلتر کردن فیلم‌های با تاریخ انتشار در گذشته
        past_movies_with_ratings = movie_list_with_ratings.filter(release_date__lte=today)

       
        # اضافه کردن فیلم‌های بر اساس تاریخ انتشار
        context['created_at'] = past_movies_with_ratings.filter(
            created_at__date__lte=today
        ).order_by('-created_at')


        context['release_date'] = past_movies_with_ratings.filter(
            release_date__lte=today
        ).order_by('-release_date')

        # # اضافه کردن فیلم‌های محبوب
        # context['popular_movies'] = past_movies_with_ratings.annotate(
        #     num_views=Count('views')
        # ).order_by('-num_views')[:10]
        # # اضافه کردن فیلم‌های با بالاترین امتیاز
        # context['top_rated_movies'] = past_movies_with_ratings.order_by('-average_rating')[:10]
        # اضافه کردن فیلم‌های پربازدید و برتر به context
        context['popular_movies'] = self.get_queryset().order_by('-num_views')[:10]
        context['top_rated_movies'] = self.get_queryset().order_by('-average_rating')[:10]

        # # اضافه کردن فیلم‌های آینده (اکران بعدی)
        # current_year = timezone.now().year
        # start_of_current_year = f"{current_year}-01-01"
        # context['coming_soon_movies'] = movie_list_with_ratings.filter(
        #     release_date__gte=start_of_current_year
        # ).order_by('release_date')[:10]
        # اضافه کردن فیلم‌هایی که به زودی اکران می‌شوند
        current_year = timezone.now().year
        start_of_current_year = f"{current_year}-01-01"
        context['coming_soon_movies'] = self.get_queryset().filter(
            release_date__gte=start_of_current_year
        ).order_by('release_date')[:10]

        # top_rated_movies = Movie.objects.order_by('-rating')[:10]  # استفاده از 'rating' به جای 'average_rating'
        # top_rated_movies_data = []

        # for movie in top_rated_movies:
        #     imdb_id = movie.imdb_id
        #     if imdb_id:
        #         omdb_data = get_movie_data(imdb_id)
        #         if omdb_data and 'imdbRating' in omdb_data and omdb_data['imdbRating'] != 'N/A':
        #             # تبدیل رتبه‌بندی به float و اضافه کردن به لیست به همراه داده‌های فیلم
        #             rating = float(omdb_data['imdbRating'])
        #             top_rated_movies_data.append((rating, movie, omdb_data))
        # # مرتب‌سازی فیلم‌ها بر اساس رتبه‌بندی IMDb به صورت نزولی
        # top_rated_movies_data.sort(reverse=True, key=lambda x: x[0])
        # # ایجاد لیست نهایی فیلم‌ها با اطلاعات مرتب‌شده
        # sorted_movies_with_data = [(movie, data) for rating, movie, data in top_rated_movies_data]
        # # اضافه کردن به context برای استفاده در template
        # context['top_rated_movies_data'] = sorted_movies_with_data
        top_rated_movies = self.get_queryset().order_by('-average_rating')[:10]
        top_rated_movies_data = [
            (movie, get_movie_data(movie.imdb_id)) for movie in top_rated_movies if movie.imdb_id
        ]
        context['top_rated_movies_data'] = top_rated_movies_data

        # اضافه کردن اطلاعات URL برای هر فیلم یا سریال
        # for movie in context['movies']:
        #     if isinstance(movie, SingleMovie):  # توجه: این فرض بر این است که SingleMovie یک زیرکلاس از Movie است
        #         movie.url = self.get_movie_url(movie)
        #     elif isinstance(movie, Series):  # توجه: این فرض بر این است که Series یک زیرکلاس از Movie است
        #         movie.url = self.get_series_url(movie)

        return context

    # def get_movie_url(self, movie):
    #     # تابعی برای دریافت URL مخصوص فیلم‌های تک قسمتی
    #     return movie.get_absolute_url()  # فرض بر این است که این متد در مدل Movie یا SingleMovie تعریف شده است

    # def get_series_url(self, series):
    #     # تابعی برای دریافت URL مخصوص سریال‌ها
    #     return series.get_absolute_url()  # فرض بر این است که این متد در مدل Series تعریف شده است

# نمایش جزئیات یک فیلم:

class AverageRatingView(View):
    def get(self, request):
        rating = AbstractBaseRating()
        rating.calculate()
        return HttpResponse("Average rating calculated.")

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'main/moviesingle.html'
    context_object_name = 'movie'
    slug_field = 'slug'  # فیلد slug که به نام 'slug' تعریف شده
    slug_url_kwarg = 'slug'  # نام کلیدی که در URL برای slug انتظار می‌رود

    def get_object(self, queryset=None):
        """Override get_object to handle custom logic."""
        obj = super().get_object(queryset=queryset)  # Get the base object

        # اگر فیلم نباید قبل از تاریخ انتشار نمایش داده شود:
        # if obj.release_date > timezone.now().date():
        #     raise Http404("This movie is not yet released.")
        
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

        Review.objects.create(movie=movie, user=user, content=content, rating=rating)

        return HttpResponseRedirect(reverse('movie_detail', kwargs={'slug': movie.slug}))


class EpisodeListView(ListView):
    model = Episode
    template_name = 'episodes/episode_list.html'
    context_object_name = 'episodes'
    
    def get_queryset(self):
        """
        فیلتر کردن قسمت‌ها بر اساس سریال مربوطه که از طریق slug در URL دریافت شده است.
        """
        movie_slug = self.kwargs.get('movie_slug')
        return Episode.objects.filter(movie__slug=movie_slug)