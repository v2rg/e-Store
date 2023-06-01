from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList


def basket(request):
    if request.session.get('basket'):
        session = request.session['basket']
        print(session)
        current_basket = []
        current_product = None
        skus = []

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
            skus.append(current_product['sku'])

        total_quantity = sum([x['basket_quantity'] for x in current_basket])  # общее количество товара в корзине
        total_sum = sum([x['product_sum'] for x in current_basket])  # общая сумма по корзине
    else:
        current_basket = None
        total_quantity = None
        total_sum = None
        skus = None

    print(skus)

    return {
        'title': 'e-Store - Корзина',
        'current_basket': current_basket,
        'total_quantity': total_quantity,
        'total_sum': total_sum,
        'skus': skus,

    }
