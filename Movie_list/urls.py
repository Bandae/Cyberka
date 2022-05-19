from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name="home-page"),

    path('register/', views.registerUser, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    # path('update-user', views.updateUser, name="update-user"),

    path('movie/<str:pk>/', views.movie, name="movie"),
    path('add-movie/', views.addMovie, name="add-movie"),
    path('update-movie/<str:pk>', views.updateMovie, name="update-movie"),
    path('delete-movie/<str:pk>', views.deleteMovie, name="delete-movie"),
    
    path('delete-review/<str:pk>', views.deleteReview, name="delete-review"),
    path('review/<str:pk>/<str:type_vote>', views.place_vote_on_review, name='vote-review')
]