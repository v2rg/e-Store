from django.core.cache import cache

from products_app.models import (Category, CpuLine, Brand, GpuModel, Socket, MemoryType)


# вертикальное меню (с категориями)
def vertical_group(request):
    # категории товаров (возвращает QuerySet)
    categories = Category.objects.all()
    cache.set('categories', categories, 60)

    # процессоры (возвращает QuerySet)
    cpus = CpuLine.objects.all().order_by('-line_name')
    cpu_brands = Brand.objects.filter(category__category_name='Процессоры').exclude(
        brand_name__exact='test_processor_brand')
    cache.set('cpus', cpus, 60)
    cache.set('cpu_brands', cpu_brands, 60)

    # видеокарты (возвращает dict)
    gpu_manufacturers = set(GpuModel.objects.values_list('gpu_brand__brand_name', flat=True))
    gpus = {}
    for manuf in gpu_manufacturers:
        gpus[manuf] = list(
            GpuModel.objects.filter(gpu_brand__brand_name=manuf).values_list('gpu_name', flat=True).order_by(
                '-gpu_brand'))
    cache.set('gpus', gpus, 60)

    # материнские платы (возвращает dict)
    mb_manufacturers = set(Socket.objects.values_list('brand_name__brand_name', flat=True))
    mbs = {}
    for manuf in mb_manufacturers:
        mbs[manuf] = list(
            Socket.objects.filter(brand_name__brand_name=manuf).values_list('socket_name', flat=True).order_by(
                '-socket_name'))
    cache.set('mbs', mbs, 60)

    # оперативная память (возвращает QuerySet)
    rams = MemoryType.objects.all().order_by('-type_name')
    cache.set('rams', rams, 60)

    return {
        'categories': cache.get('categories'),
        'cpus': cache.get('cpus'),
        'cpu_brands': cache.get('cpu_brands'),
        'gpus': cache.get('gpus'),
        'mbs': cache.get('mbs'),
        'rams': cache.get('rams'),
    }
