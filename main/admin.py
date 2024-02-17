from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Genre, Movie, Review  , IpAddress , MovieNote

# @admin.register(Actor)
# class ActorAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = ('name', )

# @admin.register(Director)
# class DirectorAdmin(admin.ModelAdmin):
#     list_display = ('full_name', )
#     search_fields = ('full_name', )
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'content', 'rating', 'approved')
    raw_id_fields = ('user', )  # اگر تعداد کاربران زیاد است، استفاده از raw_id_fields می‌تواند مفید باشد

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

class MovieNoteInline(admin.TabularInline):
    model = MovieNote
    extra = 1  # تعداد فرم‌های خالی اضافه شده برای نوت‌ها
    fields = ('note', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'director_str', 'release_date')
    list_filter = ('genres', 'release_date')
    search_fields = ('title', 'director__name', 'actor__name')
    inlines = (MovieNoteInline,)  # اضافه کردن نوت‌ها به صورت inline
    fieldsets = (
        (_("اطلاعات اصلی"), {
            'fields': ('title', 'slug', 'status', 'category', 'description')
        }),
        (_("جزئیات"), {
            'fields': ('release_date', 'director', 'actor', 'genres', 'imdb_id', 'imdb_rating', 'duration', 'poster', 'views')
        }),
        (_("متا داده‌ها"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('actor', 'genres')  # اضافه کردن 'director' به 'filter_horizontal'

    def director_str(self, obj):
        return ", ".join([director.name for director in obj.director.all()])
    director_str.short_description = _("کارگردان")

    def thumbnail(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="width: 45px; height: auto;" />', obj.poster)
        return ""
    thumbnail.short_description = _("پوستر")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            self.fieldsets = (
                (_("اطلاعات اصلی"), {
                    'fields': ('title', 'slug', 'status', 'category', 'description')
                }),
                (_("جزئیات"), {
                    'fields': ('release_date', 'genres', 'duration', 'poster', 'views')
                }),
                # مخفی کردن بخش متا داده‌ها برای غیر سوپریوزرها
            )
            # مخفی کردن فیلدهای دیگری که برای غیر سوپریوزرها نباید قابل دسترس باشند
        return form

# @admin.register(Episode)
# class EpisodeAdmin(admin.ModelAdmin):
#     list_display = ('title', 'movie', 'file')
#     list_filter = ('movie',)
#     search_fields = ('title', 'movie__title')
#     ordering = ('movie', 'title')

admin.site.register(IpAddress)