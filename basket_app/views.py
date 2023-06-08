from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import F
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

import products_app
from users_app.models import User, UserAddress
from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList
from users_app.forms import UserProfileForm, UserAddressForm
from basket_app.models import Order


# Create your views here.

@login_required
def basket(request):
    context = {
        'title': 'e-Store - Корзина',
    }

    return render(request, 'basket_app/basket.html', context)


@login_required
def basket_add(request, category_id=None, product_sku=None, quantity=None):  # добавление в корзину
    if request.session.get('basket'):  # проверяем, есть ли basket в сессии
        if request.session['basket'].get(str(product_sku)):
            request.session['basket'][str(product_sku)]['quantity'] += 1
            print('+1')
        else:
            request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1}
            messages.success(request, f'Товар {product_sku} добавлен в корзину')
            print('+sku')
    else:  # добавляется ключ basket со словарем, sku и количеством
        request.session['basket'] = {}
        request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1}
        messages.success(request, f'Товар {product_sku} добавлен в корзину')
        print('+basket, +sku')

    request.session.modified = True
    # request.session.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, product_sku=None):  # удаление из корзины
    try:
        session = request.session.get('basket')
    except ObjectDoesNotExist:
        print("request.session['basket'] не найден")
    else:
        if session:
            if session[str(product_sku)]:
                del session[str(product_sku)]
                request.session.save()
            else:
                print(f'Элемент {product_sku} не существует')
        else:
            print('basket не существует')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_update(request, product_sku=None, slug=None):  # обновление корзины
    try:
        session = request.session.get('basket')
    except ObjectDoesNotExist:
        print("request.session['basket'] не найден")
    else:
        if str(product_sku) in session:
            for category_id, category in settings.CATEGORY_ID.items():
                if session[str(product_sku)]['category_id'] == int(category_id):
                    current_product = getattr(products_app.models, category).objects.get(sku=product_sku)
                    if slug == 'incr':
                        if current_product.quantity > session[str(product_sku)]['quantity']:
                            print('incr')
                            session[str(product_sku)]['quantity'] += 1
                            request.session.modified = True
                        elif current_product.quantity == session[str(product_sku)]['quantity']:
                            print('pass')
                            pass
                    elif slug == 'decr':
                        print('decr')
                        if session[str(product_sku)]['quantity'] >= 2:
                            session[str(product_sku)]['quantity'] -= 1
                            request.session.modified = True

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def order_confirmation(request):  # подтверждение заказа
    # try:
    current_user = User.objects.get(id=request.user.id)
    # except ObjectDoesNotExist:
    #     print(f'Юзер с ID {request.user.id} не существует')
    # except MultipleObjectsReturned:
    #     print('Найдено более одного объекта')
    # else:
    current_user_address = UserAddress.objects.get(user_id=current_user.id)

    if request.method == 'POST':
        try:
            session = request.session['basket']
        except KeyError:
            print(f'Корзина пользователя {request.user} не существует')
        else:
            basket_valid_items = (
                [getattr(products_app.models, category).objects.get(sku=sku).quantity >= value['quantity']
                 if value['category_id'] == int(category_id)
                 else False
                 for category_id, category in settings.CATEGORY_ID.items()
                 for sku, value in session.items()])  # проверяем, что quantity товаров в корзине >= чем на складе

            if basket_valid_items.count(True) == len(session):
                print('Корзина валидна')

                # if request.session['basket']:
                for sku, value in request.session['basket'].items():
                    for category_id, category in settings.CATEGORY_ID.items():
                        if value['category_id'] == int(category_id):
                            current_product = getattr(products_app.models, category).objects.get(sku=sku)
                            if current_product.quantity >= value['quantity']:
                                getattr(products_app.models, category).objects.filter(sku=sku).update(
                                    quantity=F('quantity') - value['quantity'])  # уменьшаем количество товара
                                # current_product.quantity -= value['quantity']
                                # current_product.save()
                                print(f'[{category_id}, {sku}] обновлено')
                            else:
                                messages.error(request, '')

                # сохраняем заказ в таблице Order
                Order.objects.create(
                    user_id=request.user,
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],

                    postcode=request.POST['postcode'],
                    city=request.POST['city'],
                    street=request.POST['street'],
                    building=request.POST['building'],
                    floor=request.POST['floor'] if request.POST['floor'] else 0,
                    apartment=request.POST['apartment'] if request.POST['apartment'] else 0,

                    total_quantity=request.POST['total_quantity'],
                    total_sum=request.POST['total_sum'],
                    comment=request.POST['comment']
                )

                # OrderList.objects.create()

                messages.success(request, f'Заказ № {Order.objects.last().id} создан')
                print(f'Заказ № {Order.objects.last().id} создан')

                return HttpResponseRedirect(reverse('users:profile'))

            messages.error(request, f'Ошибка! В наличии меньше товара, чем в заказе')
            print(f'Заказ № {Order.objects.last().id} ОШИБКА (недостаточное кол-во)')
            return HttpResponseRedirect(reverse('basket:basket'))
    else:
        current_user_form = UserProfileForm(instance=current_user)
        current_user_address_form = UserAddressForm(instance=current_user_address)

    context = {
        'title': 'e-Store - Подтверждение заказа',
        'current_user_form': current_user_form,
        'current_user_address_form': current_user_address_form,

    }

    return render(request, 'basket_app/confirmation.html', context)
