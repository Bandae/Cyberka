from django.contrib import admin

# Register your models here.

from .models import Movie, Review, CustomUser, Vote, Comment

admin.site.register(CustomUser)
admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Vote)
admin.site.register(Comment)
