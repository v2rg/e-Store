from random import random

from django.shortcuts import render

# Create your views here.
from products_app.models import (Category, Brand, CpuLine, Socket, GpuModel, MemoryType, ProcessorList, VideoCardList,
                                 MotherboardList, MemoryList)


def index(request):
    # 8 рандомных товаров (остальное из контекст процессора)
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


def catalog(request):
    return render(request, 'products_app/catalog.html')
