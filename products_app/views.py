from random import random

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_page

import products_app
from basket_app.models import Order, OrderItem
# Create your views here.
from products_app.models import Category, ProcessorList, VideoCardList, MotherboardList, MemoryList, ProductImage
from reviews_app.models import ProductReview
from reviews_app.forms import ProductReviewForm


@cache_page(30)
def index(request):  # главная страница
    # 8 рандомных товаров
    random_products = [
        *ProcessorList.objects.filter(quantity__gt=0).order_by('?')[:2],
        *VideoCardList.objects.filter(quantity__gt=0).order_by('?')[:2],
        *MotherboardList.objects.filter(quantity__gt=0).order_by('?')[:2],
        *MemoryList.objects.filter(quantity__gt=0).order_by('?')[:2]
    ]

    context = {
        'title': 'e-Store - Главная',
        'random_products': sorted(random_products, key=lambda x: random()),  # рандом
    }

    return render(request, 'products_app/index.html', context)


def catalog(request, category_id=1, brand_name=None, line_name=None):  # каталог
    all_products = None
    category = Category.objects.get(id=category_id)

    if category_id:
        all_products = getattr(products_app.models, settings.CATEGORY_ID[str(category_id)]).objects.all()
    if brand_name:
        if category_id == 1:
            all_products = all_products.filter(brand__brand_name=brand_name)
        elif category_id == 2:
            all_products = all_products.filter(gpu__gpu_brand__brand_name=brand_name)
        elif category_id == 3:
            all_products = all_products.filter(socket__brand_name__brand_name=brand_name)
        elif category_id == 4:
            all_products = all_products.filter(type__type_name=brand_name)
    if line_name:
        if category_id == 1:
            all_products = all_products.filter(line__line_name=line_name)
        elif category_id == 2:
            all_products = all_products.filter(gpu__gpu_name=line_name)
        elif category_id == 3:
            all_products = all_products.filter(socket__socket_name=line_name)

    page_number = request.GET.get('page')
    paginator = Paginator(all_products, per_page=5)
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'e-Store - Каталог',
        'all_products': page_obj,
        'breadcrumb': {
            'category_name': category.category_name,
            'brand_name': brand_name,
            'line_name': line_name,
        },
    }

    return render(request, 'products_app/catalog.html', context)


def product(request, category_id=None, sku=None):  # карточка товара

    if request.method == 'POST':
        review_form = ProductReviewForm(data=request.POST)
        if review_form.is_valid():
            instance = review_form.save(commit=False)
            instance.product_sku = sku
            instance.user = request.user
            if instance.rating:
                pass
            else:
                instance.rating = None  # если товар не доставлен
            instance.save()
            messages.add_message(request, messages.INFO, 'Отзыв добавлен')

            return (HttpResponseRedirect(request.META['HTTP_REFERER']) if request.META.get(
                'HTTP_REFERER') else HttpResponseRedirect(reverse('index')))

    if all([category_id, sku]):
        current_product = None
        product_images = None
        in_basket = False
        reviews = None
        order_status = None

        review_form = ProductReviewForm()

        current_product = getattr(products_app.models, settings.CATEGORY_ID[str(category_id)]).objects.get(sku=sku)
        reviews = ProductReview.objects.filter(product_sku=sku).order_by('-created_datetime')
        current_product.avg_rating = reviews.average_rating()  # обновляем рейтинг товара
        current_product.save()
        product_images = ProductImage.objects.filter(sku=sku)
        review_is_exists = False if request.user.is_anonymous else reviews.filter(user=request.user).exists()
        if not review_is_exists and not request.user.is_anonymous:
            try:
                current_order_id = OrderItem.objects.get(user_id=request.user, product_sku=sku).order_id.id
            except ObjectDoesNotExist:
                pass
            else:
                order_status = Order.objects.get(id=current_order_id).status if current_order_id else None

        print(current_product)

        try:  # проверяем, что артикул есть в корзине
            session = request.session['basket']
        except KeyError:
            print('product: basket не найден')
        else:
            for i in session:
                if int(i) == current_product.sku:
                    in_basket = True
    else:
        return HttpResponseRedirect(reverse('index'))

    context = {
        'title': 'e-Store - Карточка товара',
        'current_product': current_product,
        'product_images': product_images,
        'in_basket': in_basket,
        'review_form': review_form,
        'reviews': reviews,
        'reviews_is_exists': review_is_exists,
        'order_status': order_status,

    }

    return render(request, 'products_app/product.html', context)
