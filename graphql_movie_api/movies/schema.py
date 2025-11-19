import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from datetime import date
from .models import Actor, Movie, MovieCast, Review


# Define GraphQL types for each Django model
class ActorType(DjangoObjectType):
    class Meta:
        model = Actor
        field = ('id', 'name', 'date_of_birth', 'biography', 'movies')


class MovieCastType(DjangoObjectType):
    class Meta:
        model = MovieCast
        fields = ('id', 'movie', 'actor', 'character_name')


class MovieType(DjangoObjectType):
    cast = graphene.List(MovieCastType)

    class Meta:
        model = Movie
        fields = ('id', 'title', 'summary', 'duration', 'release_date', 'trailer_url', 'actors', 'reviews')


    def resolve_cast(self, info):
        return self.moviecast_set.all()
    

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = ('id', 'movie', 'description', 'rating', 'would_recommend', 'created_at')


# Define the Query class
class Query(graphene.ObjectType):
    all_movies = graphene.List(MovieType)
    movie = graphene.Field(MovieType, id=graphene.Int(required=True))
    all_actors = graphene.List(ActorType)
    actor = graphene.Field(ActorType, id=graphene.Int(required=True))
    all_reviews = graphene.List(ReviewType)
    reviews_by_movie = graphene.List(ReviewType, movie_id=graphene.Int(required=True))

    # Resolvers - functions that fetch the data
    def resolve_all_movies(root, info):
        return Movie.objects.all()
    
    def resolve_movie(root, info, id):
        try:
            return Movie.objects.get(pk=id)
        except Movie.DoesNotExist:
            return None
        
    def resolve_all_actors(root, info):
        return Actor.objects.all()
    
    def resolve_actor(root, info, id):
        try:
            return Actor.objects.get(pk=id)
        except Actor.DoesNotExist:
            return None
        
    def resolve_all_reviews(root, info):
        return Review.objects.all()
    
    def resolve_reviews_by_movie(root, info, movie_id):
        return Review.objects.filter(movie_id=movie_id)
    


# ===== MOVIE MUTATIONS =====
class CreateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        summary = graphene.String(required=True)
        duration = graphene.Int(required=True)
        release_date = graphene.Date(required=True)
        trailer_url = graphene.String(required=True)

    movie = graphene.Field(MovieType)
    success = graphene.Boolean()
    message= graphene.String()

    def mutate(self, info, title, summary, duration, release_date, trailer_url):
        try:
            movie = Movie.objects.create(
                title=title,
                sunnary=summary,
                duration=duration,
                release_date=release_date,
                trailer_url=trailer_url
            )
            return CreateMovie(movie=movie, success=True, message="Movie created successfully.")
        except Exception as e:
            return CreateMovie(movie=None, success=False, message=str(e))


class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        summary = graphene.String()
        duration = graphene.Int()
        release_date = graphene.Date()
        trailer_url = graphene.String()

    movie = graphene.Field(MovieType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, **kwargs):
        try:
            movie = Movie.objects.get(pk=id)
            for key, value in kwargs.items():
                if value is not None:
                    setattr(movie, key, value)
            movie.save()
            return UpdateMovie(movie=movie, success=True, message="Movie updated successfully,")
        except Movie.DoesNotExist:
            return UpdateMovie(movie=None, success=False, message="Movie not found.")
        except Exception as e:
            return UpdateMovie(movie=None, success=False, message=str(e))


class DeleteMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        try:
            movie = Movie.objects.get(pk=id)
            movie.delete()
            return DeleteMovie(success=True, message="Movie deleted successfully.")
        except Movie.DoesNotExist:
            return DeleteMovie(success=False, message="Movie not found.")
        except Exception as e:
            return DeleteMovie(success=False, message=str(e))


# ===== ACTOR MUTATIONS =====


class CreateActor(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        date_of_birth = graphene.Date(required=True)
        biography = graphene.String()

    actor = graphene.Field(ActorType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, date_of_birth, biography=""):
        try:
            actor = Actor.objects.create(
                name=name,
                date_of_birth=date_of_birth,
                biography=biography
            )
            return CreateActor(actor=actor, success=True, message="Actor created successfully.")
        except Exception as e:
            return CreateActor(actor=None, success=False, message=str(e))
        
class AddActorToMovie(graphene.Mutation):
    class Arguments:
        movie_id = graphene.Int(required=True)
        actor_id = graphene.Int(required=True)
        character_name = graphene.String(required=True)

    movie_cast = graphene.Field(MovieCastType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, movie_id, actor_id, character_name):
        try:
            movie = Movie.objects.get(pk=movie_id)
            actor = Actor.objects.get(pk=actor_id)
            movie_cast = MovieCast.objects.create(
                movie=movie,
                actor=actor,
                character_name=character_name
            )
            return AddActorToMovie(
                movie_cast=movie_cast,
                success=True,
                message="Actor added to movie successfully."
            )
        except Movie.DoesNotExist:
            return AddActorToMovie(movie_cast=None, success=False, message="Movie not found.")
        except Actor.DoesNotExist:
            return AddActorToMovie(movie_cast=None, success=False, message="Actor not found.")
        except Exception as e:
            return AddActorToMovie(movie_cast=None, success=False, message=str(e))
        

# ===== REVIEW MUTATIONS =====


class CreateReview(graphene.Mutation):
    class Arguments:
        movie_id = graphene.Int(required=True)
        description = graphene.String(required=True)
        rating = graphene.Int(required=True)
        would_recommend = graphene.Boolean(required=True)

    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, movie_id, description, rating, would_recommend):
        try:
            if rating < 1 or rating > 5:
                return CreateReview(review=None, success=False, message="Rating must be between 1 and 5.")
            
            movie = Movie.objects.get(pk=movie_id)
            review = Review.objects.create(
                movie=movie,
                description=description,
                rating=rating,
                would_recommend=would_recommend
            )
            return CreateReview(review=review, success=True, message="Review created successfully.")
        except Movie.DoesNotExist:
            return CreateReview(review=None, success=False, message="Movie not found.")
        except Exception as e:
            return CreateReview(review=None, success=False, message=str(e))
        

class UpdateReview(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        description = graphene.String()
        rating = graphene.Int()
        would_recommend = graphene.Boolean()

    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, **kwargs):
        try:
            review = Review.objects.get(pk=id)

            if 'rating' in kwargs and kwargs['rating'] is not None:
                if kwargs['rating'] < 1 or kwargs['rating'] > 5:
                    return UpdateReview(
                        review=None,
                        success=False,
                        message="Rating must be between 1 and 5."
                    )
                
            for key, value in kwargs.items():
                if value is not None:
                    setattr(review, key, value)
            review.save()
            return UpdateReview(review=review, success=True, message="Review updated successfully.")
        except Review.DoesNotExist:
            return UpdateReview(review=None, success=False, message="Review not found.")
        except Exception as e:
            return UpdateReview(review=None, success=False, message=str(e))
        

# ===== MUTATION CLASS =====


class Mutation(graphene.ObjectType):
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()

    create_actor = CreateActor.Field()
    add_actor_to_movie = AddActorToMovie.Field()
    
    create_review = CreateReview.Field()
    update_review = UpdateReview.Field()



# Create the schema
schema = graphene.Schema(query=Query)

    
    



