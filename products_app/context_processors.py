from django.core.cache import cache

from products_app.models import (Category, CpuLine, Brand, GpuModel, Socket, MemoryType)


def cache_checker(name, obj, time):  # проверяем в кеше
    if not cache.get(name):
        cache.set(name, obj, time)
    else:
        return True


# вертикальное меню (категории товара)

def vertical_group(request):
    # категории товаров (возвращает QuerySet)
    if cache.get('categories'):
        pass
    else:
        categories = Category.objects.all()
        cache.set('categories', categories, 60)
        # cache_checker('categories', categories, 60)

    # процессоры (возвращает QuerySet)
    if cache.get('cpus') and cache.get('cpu_brands'):
        pass
    else:
        cpus = CpuLine.objects.all().order_by('-line_name')
        cpu_brands = Brand.objects.prefetch_related('category').filter(category__category_name='Процессоры')
        cache.set('cpus', cpus, 60)
        cache.set('cpu_brands', cpu_brands, 60)
        # cache_checker('cpus', cpus, 60)
        # cache_checker('cpu_brands', cpu_brands, 60)

    # видеокарты (возвращает dict)
    if cache.get('gpus'):
        pass
    else:
        gpu_manufacturers = set(
            GpuModel.objects.prefetch_related('gpu_brand').values_list('gpu_brand__brand_name', flat=True))
        gpus = {}
        for manuf in gpu_manufacturers:
            gpus[manuf] = list(
                GpuModel.objects.select_related('gpu_brand').prefetch_related('gpu_name').
                filter(gpu_brand__brand_name=manuf).
                values_list('gpu_name', flat=True).
                order_by('-gpu_brand'))
        cache.set('gpus', gpus, 60)
        # cache_checker('gpus', gpus, 60)

    # материнские платы (возвращает dict)
    if cache.get('mbs'):
        pass
    else:
        mb_manufacturers = set(Socket.objects.values_list('brand_name__brand_name', flat=True))
        mbs = {}
        for manuf in mb_manufacturers:
            mbs[manuf] = list(
                Socket.objects.select_related('brand_name').
                filter(brand_name__brand_name=manuf).
                values_list('socket_name', flat=True).
                order_by('-socket_name'))
        cache.set('mbs', mbs, 60)
        # cache_checker('mbs', mbs, 60)

    # оперативная память (возвращает QuerySet)
    if cache.get('rams'):
        pass
    else:
        rams = MemoryType.objects.all().order_by('-type_name')
        cache.set('rams', rams, 60)
        # cache_checker('rams', rams, 60)

    return {
        'categories': cache.get('categories'),
        'cpus': cache.get('cpus'),
        'cpu_brands': cache.get('cpu_brands'),
        'gpus': cache.get('gpus'),
        'mbs': cache.get('mbs'),
        'rams': cache.get('rams'),
    }
