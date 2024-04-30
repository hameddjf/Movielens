from .models import Actor, Director

from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_poster')
    search_fields = ('name', )

    def display_poster(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" width="80" height="125" />', obj.poster
            )
        return None
    display_poster.short_description = _('پوستر')


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'display_poster')
    search_fields = ('full_name', )

    def display_poster(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" width="80" height="125" />', obj.poster
            )
        return None
    display_poster.short_description = _('پوستر')
