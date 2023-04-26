from random import random

from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from products_app.models import (Category, Brand, CpuLine, Socket, GpuModel, MemoryType, ProcessorList, VideoCardList,
                                 MotherboardList, MemoryList)


def index(request):
    # 8 рандомных товаров (остальное из контекст-процессора)
    random_products = [
        *ProcessorList.objects.order_by('?')[:2],
        *VideoCardList.objects.order_by('?')[:2],
        *MotherboardList.objects.order_by('?')[:2],
        *MemoryList.objects.order_by('?')[:2]
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
        'all_products': page_obj,
        'breadcrumb': [category.category_name, brand_name, line_name],
    }

    return render(request, 'products_app/catalog.html', context)


def product(request, sku=None):
    return render(request, 'products_app/product.html')
