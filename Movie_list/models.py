from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from django.core.exceptions import ValidationError


#nie moge zrobic w adminie, bo to musi byc hash hasla a nie haslo
class CustomUser(AbstractUser):
    # username = models.CharField(max_length=200, null=True, unique=True)
    # email = models.EmailField(unique=True)
    # bio = models.TextField(null=True, blank=True)

    def total_score_from_own_reviews(self):
        # prawie dziala, tylko to szuka glosow uzytkownika, a nie na niego
        votes_all = Vote.objects.filter(user=self).select_related()
        upvotes = votes_all.filter(upvote=True)
        downvotes = votes_all.filter(downvote=True)
        return upvotes.count() - downvotes.count()
    
    def __str__(self):
        return self.username

    # avatar = models.ImageField(null=True, default="avatar.svg")

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []


class Movie(models.Model):
    user_added = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='user_added')
    user_last_updated = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='user_updated')
    title_pl = models.CharField(max_length=200)
    title_eng = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    #zmienic tutaj na duration jak bede umial
    runtime = models.PositiveIntegerField()
    director = models.CharField(max_length=50)
    writer = models.CharField(max_length=50)
    star1 = models.CharField(max_length=50, null=True, blank=True)
    star2 = models.CharField(max_length=50, null=True, blank=True)
    star3 = models.CharField(max_length=50, null=True, blank=True)
    
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', 'added']

    def __str__(self):
        return self.title_pl
    
    def movie_avg_rating(self):
        return Review.objects.filter(movie=self).aggregate(Avg('rating_value'))['rating_value__avg']


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    body = models.TextField()
    # value powinno byc 1-10
    rating_value = models.IntegerField()

    votes = models.ManyToManyField(CustomUser, through='Vote', related_name='user_voted')
    # total_vote_field = models.IntegerField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:50]

    def clean(self):
        super().clean()
        if self.rating_value < 1 or self.rating_value > 10:
            raise ValidationError('Out of range rating value. Must be 1-10.')

    def total_vote(self):
        votes_all = Vote.objects.filter(review=self).select_related()
        upvotes = votes_all.filter(upvote=True)
        downvotes = votes_all.filter(downvote=True)
        return upvotes.count() - downvotes.count()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'movie'], name='one_review_per_user_per_movie')]


# dziedziczenie nie dziala tak latwo w django, ze sobie skopiuje pola, uwazac
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    body = models.TextField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:50]


# class Rating(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     review = models.ForeignKey(Review, on_delete=models.CASCADE)
#     # value powinno byc 1-10
#     rating_value = models.IntegerField()

#     class Meta:
#        constraints = [models.UniqueConstraint(fields=['user', 'movie'])]


class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    # te dwa nie moga byc oba True
    upvote = models.BooleanField(default=False)
    downvote = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.upvote and self.downvote:
            raise ValidationError('An entry may not have both votes.')
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'review'], name='one_vote_per_user_per_review')]
    # def create(self):
    #     super().create()
