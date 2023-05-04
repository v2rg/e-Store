from django.contrib import auth
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

# Create your views here.
from users_app.forms import UserLoginForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            print(request.POST)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm()

    context = {
        'title': 'e-Store - Авторизация',
        'form': form
    }

    return render(request, 'users_app/login.html', context)


def registration(request):
    return render(request, 'users_app/registration.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
