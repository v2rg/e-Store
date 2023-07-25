from products_app.models import (Category, CpuLine, Brand, GpuModel, Socket, MemoryType)


# левое меню с категориями
def vertical_group(request):
    # категории товаров (возвращает QuerySet)
    categories = Category.objects.all()

    # процессоры (возвращает QuerySet)
    cpus = CpuLine.objects.all().order_by('-line_name')
    cpu_brands = Brand.objects.filter(category__category_name='Процессоры').exclude(
        brand_name__exact='test_processor_brand')

    # видеокарты (возвращает dict)
    gpu_manufacturers = set(GpuModel.objects.values_list('gpu_brand__brand_name', flat=True))
    gpus = {}
    for manuf in gpu_manufacturers:
        gpus[manuf] = list(
            GpuModel.objects.filter(gpu_brand__brand_name=manuf).values_list('gpu_name', flat=True).order_by(
                '-gpu_brand'))

    # материнские платы (возвращает dict)
    mb_manufacturers = set(Socket.objects.values_list('brand_name__brand_name', flat=True))
    mbs = {}
    for manuf in mb_manufacturers:
        mbs[manuf] = list(
            Socket.objects.filter(brand_name__brand_name=manuf).values_list('socket_name', flat=True).order_by(
                '-socket_name'))

    # оперативная память (возвращает QuerySet)
    rams = MemoryType.objects.all().order_by('-type_name')

    return {
        'categories': categories,
        'cpus': cpus,
        'cpu_brands': cpu_brands,
        'gpus': gpus,
        'mbs': mbs,
        'rams': rams,
    }
