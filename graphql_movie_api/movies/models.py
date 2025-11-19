from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Actor(models.Model):
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    biography = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Movie(models.Model):
    title = models.CharField(max_length=200)
    sunnary = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    trailer_url = models.URLField(blank=True)
    actors = models.ManyToManyField(Actor, through='MovieCast', related_name='movies')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-release_date']


class MovieCast(models.Model):
    """Junction table to store actor's alias/character name in a specific movie."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=200, help_text="Character/alias name in the movie")

    def __str__(self):
        return f"{self.actor.name} as {self.character_name} in {self.movie.title}"
    
    class Meta:
        unique_together = ('movie', 'actor')


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    description = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Rating from 1 to 5 stars")
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.movie.title} - {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']