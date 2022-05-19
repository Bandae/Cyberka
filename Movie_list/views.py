from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Count, Avg, Subquery, OuterRef, Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Movie, CustomUser, Review, Vote
from .forms import MovieForm, CustomUserCreationForm

#dodac glosowanie na recenzje + - i wstawianie komentarzy

def homePage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # przefiltrowac filmy przy uzyciu customowej filtracji z frontendu zaawansowanej

    #wyswietlic tylko kilka i kliknac zeby rozwinac

    movies = Movie.objects.filter(
        Q(title_pl__icontains=q)|
        Q(title_eng__icontains=q)|
        Q(director__icontains=q)|
        Q(writer__icontains=q)|
        Q(star1__icontains=q)|
        Q(star2__icontains=q)|
        Q(star3__icontains=q)
    ).annotate(avg_rating=Avg('review__rating_value'))

    context = {'movies': movies,}
    return render(request, 'Movie_list/home_page.html', context)

def loginPage(request):
    # page = 'login'
    # moze dekorator do tego
    if request.user.is_authenticated:
        return redirect('home-page')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home-page')
        else:
            messages.error(request, 'Username or password does not exist') 

    context = {'page': 'login'}
    return render(request, 'Movie_list/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home-page')

def registerUser(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home-page')
        else:
            messages.error(request, 'an error occured')

    context = {'form': form}
    return render(request, 'Movie_list/login_register.html', context)

def userProfile(request, pk):
    user = CustomUser.objects.get(id=pk)
    reviews = user.review_set.all()
    context = {'user': user, 'reviews': reviews,}
    return render(request, 'Movie_list/user_profile.html', context)

def movie(request, pk):
    movie = Movie.objects.get(id=pk)

    #jeszcze komentarze
    reviews = movie.review_set.all().prefetch_related(Prefetch('comment_set', to_attr='comments'))
    
    # .annotate(
    #     # subquery?
    #     # filter()
    #     # vote_total=(Count('votes__vote__upvote', filter=Q(votes__upvote=True))-Count('votes__vote__downvote', filter=Q(votes__downvote=True)))
    # )
    # .order_by('-vote_total')

    avg_rating = movie.movie_avg_rating()
    # avg_rating = reviews.aggregate(Avg('rating_value'))['rating_value__avg']


    #posortowac ocenami i wyswietlic oceny

    # jeszcze ocene zmienic
    if request.method == 'POST':
        review = Review.objects.create(
            user=request.user,
            movie=movie,
            body=request.POST.get('body'),
            rating_value=request.POST.get('rating-value'),
        )
        return redirect('movie', pk=movie.id)

    context = {'movie': movie, 'reviews': reviews, 'avg_rating': avg_rating}
    return render(request, 'Movie_list/movie.html', context)

@login_required(login_url='login')
def place_vote_on_review(request, pk, type_vote):
    review = get_object_or_404(Review, pk=pk)

    if not request.user in review.votes.all():
        Vote.objects.create(user=request.user, review=review)    
    
    through_model = Vote.objects.get(user=request.user, review=review)

    if type_vote == 'upvote':
        if through_model.upvote:
            through_model.upvote = False
        else:
            through_model.downvote = False
            through_model.upvote = True
    elif type_vote == 'downvote':
        if through_model.downvote:
            through_model.downvote = False
        else:
            through_model.upvote = False
            through_model.downvote = True
    
    through_model.save()
    
    return HttpResponseRedirect(reverse('movie', args=(review.movie.id,)))

@login_required(login_url='login')
def addMovie(request):
    form = MovieForm()

    #dodac opcje ze moze dodac tylko moderator

    if request.method == 'POST':
        # topic_name = request.POST.get('topic')
        # topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Movie.objects.create(
            user_added=request.user,
            user_last_updated=request.user,
            title_pl=request.POST.get('title_pl'),
            title_eng=request.POST.get('title_eng'),
            year=request.POST.get('year'),
            runtime=request.POST.get('runtime'),
            director=request.POST.get('director'),
            writer=request.POST.get('writer'),
            star1=request.POST.get('star1'),
            star2=request.POST.get('star2'),
            star3=request.POST.get('star3'),
            description=request.POST.get('description'),
        )
        return redirect('home-page')

    context = {'form': form}
    return render(request, 'Movie_list/movie_form.html', context)

@login_required(login_url='login')
def updateMovie(request, pk):
    movie = Movie.objects.get(id=pk)
    form = MovieForm(instance=movie)

    #dodac opcje ze moze zmieniac tylko moderator

    if request.method == 'POST':
        #czy nie nadpisze sie, jesli zostanie puste? albo moze instance w movieform robi ze sie wyswietla to co juz jest
        movie.user_last_updated = request.user,
        movie.title_pl = request.POST.get('title_pl'),
        movie.title_eng = request.POST.get('title_eng'),
        movie.year = request.POST.get('year'),
        movie.runtime = request.POST.get('runtime'),
        movie.director = request.POST.get('director'),
        movie.writer = request.POST.get('writer'),
        movie.star1 = request.POST.get('star1'),
        movie.star2 = request.POST.get('star2'),
        movie.star3 = request.POST.get('star3'),
        movie.description = request.POST.get('description'),

        movie.save()
        return redirect('home-page')

    context = {'form': form}
    return render(request, 'Movie_list/movie_form.html', context)

@login_required(login_url='login')
def deleteMovie(request, pk):
    movie = Movie.objects.get(id=pk)

    # zamiast tego moderatorzy

    # if request.user != room.host:
    #     return HttpResponse('You cant delete not owned post')
    
    if request.method == 'POST':
        movie.delete()
        return redirect('home-page')
    
    context = {'item': movie}
    return render(request, 'Movie_list/delete_old.html', context)

@login_required(login_url='login')
def deleteReview(request, pk):
    review = Review.objects.get(id=pk)

    if request.user != review.user:
        return HttpResponse('Cannot delete not owned review')
    
    if request.method == 'POST':
        review.delete()
        return redirect('home-page')
    
    context = {'item': movie}
    return render(request, 'Movie_list/delete_old.html', context)

# @login_required(login_url='login')
# def updateUser(request):
#     user = request.user
#     form = CustomUserCreationForm(instance=user)

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('user-profile', pk=user.id)
        
#     return render(request, 'Movie_list/update-user.html', {'form': form})
