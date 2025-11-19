from django.contrib import admin
from .models import Actor, Movie, MovieCast, Review

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_of_birth']
    search_fields = ['name']

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'duration']
    search_fields = ['title']
    list_filter = ['release_date']

@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ['movie', 'actor', 'character_name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['movie', 'rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend']