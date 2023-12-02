from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

import products_app
from basket_app.models import Order, OrderItem
from common.view import TitleMixin
from products_app.models import ProcessorList, Category
from users_app.forms import UserProfileForm, UserAddressForm
from users_app.models import User, UserAddress

# Create your views here.

BASKET = 50  # message level для basket


class BasketView(TitleMixin, TemplateView):  # корзина (CBV)
    template_name = 'basket_app/basket.html'
    title = 'e-Store - Корзина'


# @login_required
# def basket(request):  # корзина (заменен на CBV)
#     context = {
#         'title': 'e-Store - Корзина',
#     }
#
#     return render(request, 'basket_app/basket.html', context)


# @login_required
def basket_add(request, category_id=None, product_sku=None, product_name=None):  # добавление в корзину
    try:
        current_product = getattr(products_app.models, settings.CATEGORY_ID[str(category_id)]).objects.get(
            sku=product_sku)
        if not current_product.quantity > 0:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Товара нет в наличии')
    else:
        if request.session.get('basket'):  # проверяем, есть ли basket в сессии
            if request.session['basket'].get(str(product_sku)):
                pass
            else:
                request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1,
                                                               'product_price': float(current_product.price)}
                messages.add_message(request, BASKET, f'Товар {product_sku} добавлен в ')
                # print('+sku')
                request.session.modified = True  # session не был изменен, поэтому сохраняем вручную

        else:  # в session добавляется ключ basket со словарем (category_id, quantity, product_price)
            request.session['basket'] = {}
            request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1,
                                                           'product_price': float(current_product.price)}
            messages.add_message(request, BASKET, f'Товар {product_sku} добавлен в ')
            # print('+basket, +sku')

            # request.session.modified = True
            # request.session.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) or HttpResponseRedirect(reverse('index'))


# @login_required
def basket_remove(request, product_sku=None):  # удаление из корзины
    try:
        session = request.session.get('basket')
    except ObjectDoesNotExist:
        print("request.session['basket'] не найден")
    else:
        if session.get(str(product_sku)):
            del session[str(product_sku)]
            request.session.modified = True
        else:
            print(f'Элемент {product_sku} не существует')

    return HttpResponseRedirect(reverse('basket:basket'))


# @login_required
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
                            session[str(product_sku)]['quantity'] += 1
                            # print('incr')
                            request.session.modified = True
                        elif current_product.quantity == session[str(product_sku)]['quantity']:
                            # print('pass')
                            pass
                        else:
                            session[str(product_sku)]['quantity'] = current_product.quantity
                            messages.ERROR(request, 'В наличии меньше товара')
                    elif slug == 'decr':
                        if session[str(product_sku)]['quantity'] >= 2:
                            session[str(product_sku)]['quantity'] -= 1
                            # print('decr')
                            request.session.modified = True

    return HttpResponseRedirect(reverse('basket:basket'))


@login_required
def order_confirmation(request):  # подтверждение заказа

    current_user_form = None
    current_user_address_form = None

    try:
        current_user = User.objects.get(id=request.user.id)
    except ObjectDoesNotExist:
        print(f'Юзер с ID {request.user.id} не существует')
    else:
        try:
            current_user_address = UserAddress.objects.get(user_id=current_user.id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('users:profile'))
        else:
            if request.method == 'POST':
                current_user_form = UserProfileForm(data=request.POST)
                current_user_address_form = UserAddressForm(data=request.POST)
                if current_user_form.is_valid() and current_user_address_form.is_valid():
                    try:
                        session = request.session['basket']
                    except KeyError:
                        print(f'Корзина пользователя {request.user} не существует')
                    else:
                        if session:
                            basket_valid_items = (
                                [getattr(products_app.models, category).objects.get(sku=sku).quantity >= value[
                                    'quantity']
                                 if value['category_id'] == int(category_id)
                                 else False
                                 for category_id, category in settings.CATEGORY_ID.items()
                                 for sku, value in session.items()]
                            )  # проверяем, что quantity товаров в корзине >= чем на складе

                            if basket_valid_items.count(True) == len(session):
                                print('Корзина валидна')

                                for sku, value in request.session['basket'].items():
                                    for category_id, category in settings.CATEGORY_ID.items():
                                        if value['category_id'] == int(category_id):
                                            current_product = getattr(products_app.models, category).objects.get(
                                                sku=sku)

                                            # уменьшаем количество товара и меняем статус, если остаток < 1
                                            if current_product.quantity >= value['quantity']:
                                                current = getattr(products_app.models, category).objects.get(sku=sku)
                                                current.quantity = current.quantity - value['quantity']
                                                # current.active = False if current.quantity - value[
                                                #     'quantity'] == 0 else current.active
                                                current.save(update_fields=['quantity'])

                                                # getattr(products_app.models, category).objects.filter(sku=sku).update(
                                                #     quantity=F('quantity') - value['quantity'],
                                                #     active=False if (F('quantity') - value['quantity']) < 1 else True
                                                # )  # уменьшаем количество товара

                                                print(f'[{category_id}, {sku}] обновлено')
                                            else:
                                                messages.add_message(request, messages.ERROR, '')

                                # сохраняем заказ в таблице Order
                                # print(current_user_form.cleaned_data)
                                # print(current_user_address_form.cleaned_data)
                                order = Order.objects.create(
                                    user_id=request.user,
                                    first_name=current_user_form.cleaned_data['first_name'],
                                    last_name=current_user_form.cleaned_data['last_name'],

                                    postcode=current_user_address_form.cleaned_data['postcode'],
                                    city=current_user_address_form.cleaned_data['city'],
                                    street=current_user_address_form.cleaned_data['street'],
                                    building=current_user_address_form.cleaned_data['building'],
                                    floor=current_user_address_form.cleaned_data['floor'] if request.POST[
                                        'floor'] else '-',
                                    apartment=current_user_address_form.cleaned_data['apartment'] if request.POST[
                                        'apartment'] else '-',

                                    total_quantity=request.POST['total_quantity'],
                                    total_sum=request.POST['total_sum'],
                                    comment=request.POST['comment']
                                )

                                # сохраняем содержимое заказа в таблицу OrderItem
                                current_order = Order.objects.filter(user_id=request.user).order_by(
                                    'created_datetime').last()
                                for sku, value in session.items():
                                    OrderItem.objects.create(
                                        order_id=current_order,
                                        user_id=request.user,
                                        product_category=Category.objects.get(id=value['category_id']),
                                        product_sku=sku,
                                        quantity=value['quantity'],
                                        price=value['product_price']
                                    )

                                order_items = OrderItem.objects.filter(order_id=current_order).count()
                                if len(session) == order_items:
                                    del request.session['basket']  # удаляем корзину
                                    order.send_confirmation_email()
                                    messages.add_message(request, messages.SUCCESS,
                                                         f'Заказ № {Order.objects.last().id} создан')
                                    print(f'Заказ № {current_order} создан')
                                    return HttpResponseRedirect(reverse('users:orders'))
                                else:
                                    Order.objects.get(
                                        id=current_order).delete()  # удаляем запись в таблице Order, при ошибке
                                    messages.add_message(request, messages.ERROR, 'Ошибка! Заказ не создан')
                                    print(f'Заказ № {current_order} ОШИБКА (заказ не создан, запись из order удалена)')
                                    return HttpResponseRedirect(reverse('basket:basket'))

                            messages.add_message(
                                request, messages.ERROR, f'Ошибка! В наличии меньше товара, чем в заказе')
                            print(f'Заказ № {Order.objects.last().id} ОШИБКА (недостаточное кол-во)')
                            return HttpResponseRedirect(reverse('basket:basket'))
                        else:
                            return HttpResponseRedirect(reverse('index'))
                else:
                    messages.add_message(request, messages.ERROR, 'Форма заполнена неверно')

            else:  # request.GET
                if request.session.get('basket'):
                    current_user_form = UserProfileForm(instance=current_user)
                    current_user_address_form = UserAddressForm(instance=current_user_address)
                else:
                    return HttpResponseRedirect(reverse('index'))

    context = {
        'title': 'e-Store - Подтверждение заказа',
        'current_user_form': current_user_form,
        'current_user_address_form': current_user_address_form,

    }

    return render(request, 'basket_app/confirmation.html', context)


@login_required
def payment(request, order_id=None):  # оплата заказа
    if request.method == 'GET':
        try:
            current_order = Order.objects.get(id=order_id, user_id=request.user)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('index'))
        else:
            # current_order_items = OrderItem.objects.filter(order_id=order_id, user_id=request.user)
            context = {
                'current_order': current_order,
                # 'current_order_items': current_order_items,
            }
            return render(request, 'basket_app/payment.html', context)


@login_required
def payment_confirmation(request, order_id=None):  # подтверждение оплаты
    if request.method == 'GET':
        try:
            current_order = Order.objects.get(id=order_id, user_id=request.user)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('index'))
        else:
            if current_order.status == 'created':
                current_order.status = 'paid'
                current_order.save()
                messages.info(request, f'Заказ №{order_id} успешно оплачен')
                return HttpResponseRedirect(reverse('users:orders'))
            else:
                return HttpResponseRedirect(reverse('users:orders'))
