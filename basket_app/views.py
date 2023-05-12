from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList


# Create your views here.

def basket(request):
    if request.session.get('basket'):
        session = request.session['basket']
        # print(session)
        current_basket = []
        current_product = None

        for sku, value in session.items():
            if value['category_id'] == 1:
                current_product = ProcessorList.objects.values().get(sku=int(sku))
            elif value['category_id'] == 2:
                current_product = VideoCardList.objects.values().get(sku=int(sku))
            elif value['category_id'] == 3:
                current_product = MotherboardList.objects.values().get(sku=int(sku))
            elif value['category_id'] == 4:
                current_product = MemoryList.objects.values().get(sku=int(sku))

            current_product['basket_quantity'] = value['quantity']  # количество товара по одной позиции
            current_product['product_sum'] = current_product['price'] * current_product[
                'basket_quantity']  # сумма одной позиции
            current_basket.append(current_product)

        total_quantity = sum([x['basket_quantity'] for x in current_basket])  # общее количество товара в корзине
        total_sum = sum([x['product_sum'] for x in current_basket])  # общая сумма по корзине
    else:
        current_basket = None
        total_quantity = None
        total_sum = None

    print(current_basket)

    context = {
        'title': 'e-Store - Корзина',
        'current_basket': current_basket,
        'total_quantity': total_quantity,
        'total_sum': total_sum,
    }

    return render(request, 'basket_app/basket.html', context)


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


def basket_update(request):
    ...
