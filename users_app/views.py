from django.contrib import auth
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse

# Create your views here.
from users_app.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from users_app.models import User


def login(request):  # авторизация
    if request.method == 'POST':
        login_form = UserLoginForm(data=request.POST)
        if login_form.is_valid():
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        login_form = UserLoginForm()

    context = {
        'title': 'e-Store - Авторизация',
        'login_form': login_form
    }

    return render(request, 'users_app/login.html', context)


def registration(request):  # регистрация
    if request.method == 'POST':
        register_form = UserRegistrationForm(data=request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect(reverse('users:login'))
    else:
        register_form = UserRegistrationForm()

    context = {
        'title': 'e-Store - Регистрация',
        'register_form': register_form
    }

    return render(request, 'users_app/registration.html', context)


def logout(request):  # логаут
    auth.logout(request)
    return HttpResponsePermanentRedirect(reverse('users:login'))


def profile(request):  # профиль пользователя
    current_user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        profile_form = UserProfileForm(instance=current_user, data=request.POST, files=request.FILES)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        profile_form = UserProfileForm(instance=current_user)

    context = {
        'title': 'e-Store - Профиль',
        'current_user_avatar': current_user.avatar,
        'profile_form': profile_form
    }
    return render(request, 'users_app/profile.html', context)
