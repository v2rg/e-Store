from django.shortcuts import render


# Create your views here.

def index(request):
    # # категории товаров
    # categories = Category.objects.all()
    #
    # # 8 рандомных товаров
    # random_processors = Processor.objects.order_by('?')[:6]
    # random_motherboards = ...
    # random_videocards = ...
    # random_memories = ...
    #
    # alls = dict()
    #
    # for category in Category.objects.all():
    #     alls[category.category] = Brand.objects.filter(category__category=category).values()
    #
    # print(alls)
    #
    # context = {
    #     'categories': categories,
    #     'products': random_processors,
    #     'alls': alls,
    # }
    #
    return render(request, 'products_app/index.html')
