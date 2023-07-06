import products_app
from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList
from users_app.models import UserAddress


def basket(request):
    if request.session.get('basket'):
        if not request.user.is_anonymous:
            UserAddress.objects.get_or_create(user_id=request.user)
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

            current_product['basket_quantity'] = (
                current_product['quantity'] if value['quantity'] > current_product['quantity']
                else value['quantity'])  # количество товара по одной позиции
            current_product['product_sum'] = (
                    current_product['price'] * current_product['basket_quantity'])  # сумма одной позиции

            current_basket.append(current_product)
            skus.append(current_product['sku'])

        total_quantity = sum([x['basket_quantity'] for x in current_basket])  # общее количество товара в корзине
        total_sum = sum([x['product_sum'] for x in current_basket])  # общая сумма по корзине
        basket_is_active = False if any(x['quantity'] < 1 for x in current_basket) else True
    else:
        current_basket = None
        total_quantity = None
        total_sum = None
        skus = None
        basket_is_active = None

    return {
        'title': 'e-Store - Корзина',
        'current_basket': current_basket,
        'total_quantity': total_quantity,
        'total_sum': total_sum,
        'skus': skus,
        'basket_is_active': basket_is_active,

    }
