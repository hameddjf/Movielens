from django.contrib import admin
from .models import Actor, Director

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    search_fields = ('full_name', )