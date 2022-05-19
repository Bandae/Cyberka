from django.forms import IntegerField, ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Movie, CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

class MovieForm(ModelForm):
    # rating = IntegerField()
    #jakis clean tutaj wlacznie z odpowiednimi ocenami, a nie bo przy pisaniu recenzji
    class Meta:
        model = Movie
        fields = '__all__'
        exclude = ['user_added', 'user_last_updated', 'ratings']


# class UserForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['avatar', 'name', 'username', 'email', 'bio']