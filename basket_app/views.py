from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList


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
    return render(request, 'basket_app/confirmation.html')
