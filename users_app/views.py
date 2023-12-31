from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import CreateView, ListView

import products_app
from basket_app.models import Order, OrderItem
from common.view import TitleMixin
# Create your views here.
from users_app.forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserAddressForm
from users_app.models import User, UserAddress, EmailVerification


class UserLoginView(TitleMixin, LoginView):  # авторизация (CBV)
    template_name = 'users_app/login.html'
    authentication_form = UserLoginForm
    title = 'e-Store - Авторизация'

    def form_valid(self, form):
        user = auth.authenticate(username=self.request.POST['username'], password=self.request.POST['password'])
        if user.is_verified_email:  # проверка подтвержденного имейла
            auth.login(self.request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.add_message(self.request, messages.ERROR, 'Аккаунт не подтвержден')
            return HttpResponseRedirect(reverse('users:login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['login_form'] = self.get_form()
        return context


# def login(request):  # авторизация (заменен на CBV)
#     if request.method == 'POST':
#         login_form = UserLoginForm(data=request.POST)
#         if login_form.is_valid():
#             user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
#             if user.is_verified_email:  # проверка подтвержденного имейла
#                 auth.login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 messages.add_message(request, messages.ERROR, 'Аккаунт не подтвержден')
#                 return HttpResponseRedirect(reverse('users:login'))
#     else:
#         login_form = UserLoginForm()
#
#     context = {
#         'title': 'e-Store - Авторизация',
#         'login_form': login_form
#     }
#
#     return render(request, 'users_app/login.html', context)


class UserRegistrationView(TitleMixin, CreateView):  # регистрация (CBV)
    template_name = 'users_app/registration.html'
    form_class = UserRegistrationForm
    title = 'e-Store - Регистрация'

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.SUCCESS,
                             'Требуется подтверждение аккаунта. Письмо отправлено на почту')
        return HttpResponseRedirect(reverse('users:login'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['register_form'] = self.get_form()
        return context


# def registration(request):  # регистрация (заменен на CBV)
#     if request.method == 'POST':
#         register_form = UserRegistrationForm(data=request.POST)
#         if register_form.is_valid():
#             register_form.save()
#             messages.add_message(request, messages.SUCCESS,
#                                  'Требуется подтверждение аккаунта. Письмо отправлено на почту')
#             return HttpResponseRedirect(reverse('users:login'))
#     else:
#         register_form = UserRegistrationForm()
#
#     context = {
#         'title': 'e-Store - Регистрация',
#         'register_form': register_form
#     }
#
#     return render(request, 'users_app/registration.html', context)


def verify_email(request, username=None, user_uuid=None):  # подтверждение почты
    try:
        verifying_user = EmailVerification.objects.get(user__username=username, uuid_code=user_uuid)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Пользователь не найден')
        return HttpResponseRedirect(reverse('users:login'))
    else:
        if verifying_user.expiration > now():
            User.objects.filter(username=verifying_user).update(is_verified_email=True)
            UserAddress.objects.create(user_id=verifying_user.user)  # создается запись в UserAddress
            messages.add_message(request, messages.SUCCESS, 'Аккаунт успешно подтвержден')
            return HttpResponseRedirect(reverse('users:login'))
        else:
            User.objects.get(username=verifying_user).delete()
            messages.add_message(request, messages.ERROR, 'Пользователь не найден')
            return HttpResponseRedirect(reverse('users:login'))


# @login_required
# def logout(request):  # логаут (заменен на CBV)
#     auth.logout(request)
#     return HttpResponsePermanentRedirect(reverse('users:login'))


@login_required
def profile(request):  # профиль пользователя

    profile_form = None
    profile_address_form = None

    try:
        current_user = User.objects.get(id=request.user.id)
    except ObjectDoesNotExist:
        print(f'Юзер с ID {request.user.id} не существует')
    else:
        # добавляет запись в таблицу UserAddress, когда пользователь впервые заходит в профиль. Или получает адрес
        current_user_address, _ = UserAddress.objects.get_or_create(user_id=request.user)

        if request.method == 'POST':
            if request.POST.get('user'):
                profile_form = UserProfileForm(instance=current_user, data=request.POST, files=request.FILES)
                if profile_form.is_valid():
                    profile_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Профиль обновлен')
                else:
                    print('Ошибка валидации UserProfileForm')
            elif request.POST.get('address'):
                profile_address_form = UserAddressForm(instance=current_user_address, data=request.POST)
                if profile_address_form.is_valid():
                    profile_address_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Адрес обновлен')
                else:
                    messages.add_message(request, messages.ERROR, 'Индекс должен содержать только цифры')
                    print('Ошибка валидации UserAddressForm')

            return HttpResponseRedirect(reverse('users:profile'))

        else:
            profile_form = UserProfileForm(instance=current_user)
            profile_address_form = UserAddressForm(instance=current_user_address)

    context = {
        'title': 'e-Store - Профиль',
        # 'current_user_avatar': current_user.avatar,
        'profile_form': profile_form,
        'profile_form_address': profile_address_form,

    }
    return render(request, 'users_app/profile.html', context)


class OrdersView(TitleMixin, ListView):  # история заказов (CBV)
    model = Order
    template_name = 'users_app/orders.html'
    title = 'e-Store - Заказы'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user_orders'] = self.get_queryset()
        context['not_paid'] = self.get_queryset().filter(status='created')
        return context


# @login_required
# def orders(request):  # история заказов (заменен на CBV)
#     user_orders = Order.objects.filter(user_id=request.user).order_by('-id')
#
#     context = {
#         'title': 'e-Store - Заказы',
#         'user_orders': user_orders,
#
#     }
#
#     return render(request, 'users_app/orders.html', context)


@login_required
def order(request, order_id=None):  # содержимое заказа
    try:
        order_data = Order.objects.get(user_id=request.user, id=order_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('users:orders'))
    else:
        order_items = OrderItem.objects.filter(user_id=request.user, order_id=order_id).values()

        for ind, order_item in enumerate(order_items):  # добавляем название товара в QuerySet (список)
            order_items[ind]['product_name'] = getattr(
                products_app.models, settings.CATEGORY_ID[str(order_item['product_category_id'])]).objects.get(
                sku=order_item['product_sku']).name
            order_items[ind]['sku_total_price'] = order_item['quantity'] * order_item['price']

        total_price = sum([x['sku_total_price'] for x in order_items])

    context = {
        'title': 'Содержимое заказа',
        'order_id': order_id,
        'order_data': order_data,
        'order_items': order_items,
        'total_price': total_price,

    }

    return render(request, 'users_app/order.html', context)
