from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse

# Create your views here.
from users_app.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserAddressForm
from users_app.models import User, UserAddress


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


@login_required
def logout(request):  # логаут
    auth.logout(request)
    return HttpResponsePermanentRedirect(reverse('users:login'))


@login_required()
def profile(request):  # профиль пользователя

    current_user = User.objects.get(id=request.user.id)
    # добавляет запись в таблицу UserAddress, когда пользователь впервые заходит в профиль, или получает адрес
    current_user_address, _ = UserAddress.objects.get_or_create(user_id=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(instance=current_user, data=request.POST, files=request.FILES)
        if profile_form.is_valid():
            profile_form.save()

        # if current_user_address:
        profile_address_form = UserAddressForm(instance=current_user_address, data=request.POST)
        if profile_address_form.is_valid():
            profile_address_form.save()

        messages.success(request, ' обновлен')

        return HttpResponseRedirect(reverse('users:profile'))

    else:
        profile_form = UserProfileForm(instance=current_user)
        profile_address_form = UserAddressForm(instance=current_user_address)

    context = {
        'title': 'e-Store - Профиль',
        # 'current_user_avatar': current_user.avatar,
        'profile_form': profile_form,
        'profile_form_address': profile_address_form
    }
    return render(request, 'users_app/profile.html', context)
