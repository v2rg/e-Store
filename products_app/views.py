from random import random

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from products_app.models import (Category, Brand, CpuLine, Socket, GpuModel, MemoryType, ProcessorList, VideoCardList,
                                 MotherboardList, MemoryList, ProductImage)


def index(request):
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


def catalog(request, category_id=1, brand_name=None, line_name=None):
    all_products = None
    category = Category.objects.get(id=category_id)

    if category_id:
        if category.category_name == 'Процессоры':
            all_products = ProcessorList.objects.all()
        elif category.category_name == 'Видеокарты':
            all_products = VideoCardList.objects.all()
        elif category.category_name == 'Материнские платы':
            all_products = MotherboardList.objects.all()
        elif category.category_name == 'Оперативная память':
            all_products = MemoryList.objects.all()
    if brand_name:
        if category.category_name == 'Процессоры':
            all_products = all_products.filter(brand__brand_name=brand_name)
        elif category.category_name == 'Видеокарты':
            all_products = all_products.filter(gpu__gpu_brand__brand_name=brand_name)
        elif category.category_name == 'Материнские платы':
            all_products = all_products.filter(socket__brand_name__brand_name=brand_name)
        elif category.category_name == 'Оперативная память':
            all_products = all_products.filter(type__type_name=brand_name)
    if line_name:
        if category.category_name == 'Процессоры':
            all_products = all_products.filter(line__line_name=line_name)
        elif category.category_name == 'Видеокарты':
            all_products = all_products.filter(gpu__gpu_name=line_name)
        elif category.category_name == 'Материнские платы':
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


def product(request, category_id=None, sku=None):
    current_product = None
    product_images = None
    in_basket = False

    if all([category_id, sku]):
        product_images = ProductImage.objects.filter(sku=sku)

        if category_id == 1:
            current_product = ProcessorList.objects.get(sku=sku)
        elif category_id == 2:
            current_product = VideoCardList.objects.get(sku=sku)
        elif category_id == 3:
            current_product = MotherboardList.objects.get(sku=sku)
        elif category_id == 4:
            current_product = MemoryList.objects.get(sku=sku)

        try:
            session = request.session['basket']
        except KeyError:
            print('product: basket не найден')
        else:
            for i in request.session['basket']:
                if int(i) == current_product.sku:
                    in_basket = True

    context = {
        'title': 'e-Store - Карточка товара',
        'current_product': current_product,
        'product_images': product_images,
        'in_basket': in_basket,
    }

    return render(request, 'products_app/product.html', context)
