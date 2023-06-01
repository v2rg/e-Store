from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

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
def basket_add(request, category_id=None, product_sku=None, quantity=None):  # добавление в корзину (sku, quantity)
    if request.session.get('basket'):  # проверяем, есть ли basket в сессии
        if request.session['basket'].get(str(product_sku)):
            request.session['basket'][str(product_sku)]['quantity'] += 1
            print('+1')
        else:
            request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1}
            print('+sku')
    else:  # добавляется ключ basket со словарем, sku и количеством
        request.session['basket'] = {}
        request.session['basket'][str(product_sku)] = {'category_id': category_id, 'quantity': 1}
        print('+basket, +sku')

    request.session.modified = True
    # request.session.save()

    print(request.session.get('basket'))
    print(request.session.items())

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, product_sku=None):
    session = request.session.get('basket')
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
def basket_update(request, product_sku=None, slug=None):
    session = request.session.get('basket')
    # print(session)
    if session:
        if str(product_sku) in session:
            if slug == 'incr':
                session[str(product_sku)]['quantity'] += 1
                request.session.modified = True
            elif slug == 'decr':
                if session[str(product_sku)]['quantity'] >= 2:
                    session[str(product_sku)]['quantity'] -= 1
                    request.session.modified = True

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def order_confirmation(request):
    try:
        current_user = User.objects.get(id=request.user.id)
        current_user_address = UserAddress.objects.get(user_id=current_user.id)
    except ObjectDoesNotExist:
        print(f'Объект {request.user.id} не существует')
    except MultipleObjectsReturned:
        print('Найдено более одного объекта')
    else:
        if request.method == 'POST':
            # print(request.POST)
            # print(request.session['basket'])
            for sku, value in request.session['basket'].items():
                if value['category_id'] == 1:
                    current_product = ProcessorList.objects.get(sku=sku)
                    if current_product.quantity >= value['quantity']:
                        current_product.quantity -= value['quantity']
                        current_product.save()
                        print(f'{sku} обновлено')
                    else:
                        messages.error(request, '')

                print(sku, value)

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
            print('OK')

            return HttpResponseRedirect(reverse('users:profile'))
        else:
            current_user_form = UserProfileForm(instance=current_user)
            current_user_address_form = UserAddressForm(instance=current_user_address)

    context = {
        'title': 'e-Store - Подтверждение заказа',
        'current_user_form': current_user_form,
        'current_user_address_form': current_user_address_form,

    }

    return render(request, 'basket_app/confirmation.html', context)
