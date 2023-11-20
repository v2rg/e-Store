from random import random

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
# from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView
from django.views.generic.base import ContextMixin

import products_app
from basket_app.models import OrderItem
from common.view import TitleMixin
# Create your views here.
from products_app.models import Category, ProcessorList, VideoCardList, MotherboardList, MemoryList, ProductImage
from reviews_app.forms import ProductReviewForm
from reviews_app.models import ProductReview


class IndexView(TitleMixin, TemplateView):  # главная страница (CBV)
    template_name = 'products_app/index.html'
    title = 'e-Store - Главная'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if not cache.get('random_products'):
            random_products = [
                *ProcessorList.objects.select_related(
                    'line', 'socket', 'memory_type').filter(quantity__gt=0).order_by('?')[:2],
                *VideoCardList.objects.select_related(
                    'gpu', 'pci_version').filter(quantity__gt=0).order_by('?')[:2],
                *MotherboardList.objects.select_related(
                    'socket', 'form_factor', 'chipset',
                    'memory_type', 'pci_version').filter(quantity__gt=0).order_by('?')[:2],
                *MemoryList.objects.select_related('type').filter(quantity__gt=0).order_by('?')[:2]]
            cache.set('random_products', sorted(random_products, key=lambda x: random()), 30)
        context['random_products'] = cache.get('random_products')

        return context


# def index(request):  # главная страница (заменен на CBV)
#     # 8 рандомных товаров (в кэш на 30 секунд)
#     if not cache.get('random_products'):
#         random_products = [
#             *ProcessorList.objects.filter(quantity__gt=0).order_by('?')[:2],
#             *VideoCardList.objects.filter(quantity__gt=0).order_by('?')[:2],
#             *MotherboardList.objects.filter(quantity__gt=0).order_by('?')[:2],
#             *MemoryList.objects.filter(quantity__gt=0).order_by('?')[:2]
#         ]
#         cache.set('random_products', sorted(random_products, key=lambda x: random()), 30)
#
#     context = {
#         'title': 'e-Store - Главная',
#         'random_products': cache.get('random_products'),  # рандом
#     }
#
#     return render(request, 'products_app/index.html', context)


class CatalogView(ListView):  # каталог (CBV)
    template_name = 'products_app/catalog.html'
    paginate_by = 5
    sort_method = None
    sort_by = None

    def filtering(self, queryset):  # фильтрация
        if self.request.session.get('filtering'):
            if self.request.session['filtering']['high_rating']:
                queryset = queryset.filter(avg_rating__gte=4)
            if self.request.session['filtering']['price_from']:
                queryset = queryset.filter(price__gte=self.request.session['filtering']['price_from'])
            if self.request.session['filtering']['price_to']:
                queryset = queryset.filter(price__lte=self.request.session['filtering']['price_to'])

        return queryset

    def get_queryset(self):
        # queryset = super().get_queryset()
        # print(self.request.GET)

        if not self.kwargs.get('category_id'):  # дефолтная категория (processors)
            self.kwargs['category_id'] = 1

        try:
            queryset = getattr(products_app.models, settings.CATEGORY_ID[str(self.kwargs['category_id'])]).objects.all()
        except KeyError:
            pass
        else:
            # фильтрация
            if self.request.GET.get('high_rating') or self.request.GET.get('price_from') or self.request.GET.get(
                    'price_to'):
                self.request.session['filtering'] = {
                    'high_rating': self.request.GET.get('high_rating'),
                    'price_from': self.request.GET.get('price_from'),
                    'price_to': self.request.GET.get('price_to')}
                queryset = self.filtering(queryset)
            elif self.request.GET.get('page'):
                queryset = self.filtering(queryset)
            else:
                try:
                    del self.request.session['filtering']
                except KeyError:
                    pass

            ''''''

            if self.kwargs.get('brand_name'):  # фильтрация по бренду
                if self.kwargs['category_id'] == 1:
                    queryset = queryset.filter(brand__brand_name=self.kwargs['brand_name'])
                elif self.kwargs['category_id'] == 2:
                    queryset = queryset.filter(gpu__gpu_brand__brand_name=self.kwargs['brand_name'])
                elif self.kwargs['category_id'] == 3:
                    queryset = queryset.filter(socket__brand_name__brand_name=self.kwargs['brand_name'])
                elif self.kwargs['category_id'] == 4:
                    queryset = queryset.filter(type__type_name=self.kwargs['brand_name'])

            if self.kwargs.get('line_name'):  # фильтрация по линейке
                if self.kwargs['category_id'] == 1:
                    queryset = queryset.filter(line__line_name=self.kwargs['line_name'])
                elif self.kwargs['category_id'] == 2:
                    queryset = queryset.filter(gpu__gpu_name=self.kwargs['line_name'])
                elif self.kwargs['category_id'] == 3:
                    queryset = queryset.filter(socket__socket_name=self.kwargs['line_name'])

            # if len(queryset) == 0:  # обработчик NoReverseMatch
            #     raise Http404

            try:  # сортировка
                self.sort_method = self.request.session['catalog_sorting']['sorting_method']
                self.sort_by = self.request.session['catalog_sorting']['sorting_by']
            except KeyError:
                pass
            else:
                queryset = (queryset.order_by(self.sort_by + self.sort_method) if self.sort_method in ('name', 'price')
                            else queryset.order_by('-' + self.sort_method, 'name'))

            return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        context = super().get_context_data()
        context['path_category'] = self.kwargs['category_id']
        context['sort_method'] = self.sort_method if self.sort_method else None
        context['sort_by'] = self.sort_by if self.sort_by else None
        ''''''
        context['filtration'] = {
            'high_rating': (
                True
                if self.request.session.get('filtering') and self.request.session['filtering'].get('high_rating')
                else False
            ),
            'low_price': (
                self.request.session['filtering']['price_from']
                if self.request.session.get('filtering') and self.request.session['filtering'].get('price_from')
                else False
            ),
            'low_price_placeholder': (
                int(queryset.order_by('price')[0].price)
                if queryset
                else self.request.GET.get('price_from')
            ),
            'high_price': (
                self.request.session['filtering']['price_to']
                if self.request.session.get('filtering') and self.request.session['filtering'].get('price_to')
                else False
            ),
            'high_price_placeholder': (
                int(queryset.order_by('-price')[0].price) + 1
                if queryset
                else self.request.GET.get('price_to')
            )
        }

        # context['high_rating'] = (
        #     True
        #     if self.request.session.get('filtering') and self.request.session['filtering'].get('high_rating')
        #     else False
        # )
        # context['low_price_placeholder'] = (
        #     int(queryset.order_by('price')[0].price)
        #     if queryset
        #     else self.request.GET.get('price_from')
        # )
        # context['low_price'] = (
        #     self.request.session['filtering']['price_from']
        #     if self.request.session.get('filtering') and self.request.session['filtering'].get('price_from')
        #     else False
        # )
        # context['high_price_placeholder'] = (
        #     int(queryset.order_by('-price')[0].price) + 1
        #     if queryset
        #     else self.request.GET.get('price_to')
        # )
        # context['high_price'] = (
        #     self.request.session['filtering']['price_to']
        #     if self.request.session.get('filtering') and self.request.session['filtering'].get('price_to')
        #     else False
        # )

        context['breadcrumb'] = {
            'category_name': Category.objects.get(id=self.kwargs.get('category_id')).category_name,
            'brand_name': self.kwargs.get('brand_name'),
            'line_name': self.kwargs.get('line_name'),
        }

        return context


# def catalog(request, category_id=1, brand_name=None, line_name=None):  # каталог (заменен на CBV)
#     all_products = None
#     category = Category.objects.get(id=category_id)
#
#     if category_id:
#         all_products = getattr(products_app.models, settings.CATEGORY_ID[str(category_id)]).objects.all()
#     if brand_name:
#         if category_id == 1:
#             all_products = all_products.filter(brand__brand_name=brand_name)
#         elif category_id == 2:
#             all_products = all_products.filter(gpu__gpu_brand__brand_name=brand_name)
#         elif category_id == 3:
#             all_products = all_products.filter(socket__brand_name__brand_name=brand_name)
#         elif category_id == 4:
#             all_products = all_products.filter(type__type_name=brand_name)
#     if line_name:
#         if category_id == 1:
#             all_products = all_products.filter(line__line_name=line_name)
#         elif category_id == 2:
#             all_products = all_products.filter(gpu__gpu_name=line_name)
#         elif category_id == 3:
#             all_products = all_products.filter(socket__socket_name=line_name)
#
#     page_number = request.GET.get('page')
#     paginator = Paginator(all_products, per_page=5)
#     page_obj = paginator.get_page(page_number)
#
#     context = {
#         # 'title': 'e-Store - Каталог',
#         'all_products': page_obj,
#         'breadcrumb': {
#             'category_name': category.category_name,
#             'brand_name': brand_name,
#             'line_name': line_name,
#         },
#     }
#
#     return render(request, 'products_app/catalog.html', context)


def sorting_method(request, method=None):  # сортировка в каталоге
    if method in settings.SORTING_METHODS:
        try:
            sort_method = request.session['catalog_sorting']['sorting_method']
            sort_by = request.session['catalog_sorting']['sorting_by']
        except KeyError:
            request.session['catalog_sorting'] = {'sorting_method': method, 'sorting_by': ''}
            request.session.modified = True
        else:
            if sort_method == method:  # asc/desc
                if sort_by == '':
                    request.session['catalog_sorting']['sorting_by'] = '-'
                    request.session.modified = True
                elif sort_by == '-':
                    request.session['catalog_sorting']['sorting_by'] = ''
                    request.session.modified = True
            else:
                request.session['catalog_sorting'] = {'sorting_method': method, 'sorting_by': ''}
                request.session.modified = True
        finally:
            try:
                ref = request.META['HTTP_REFERER']
            except KeyError:
                return HttpResponseRedirect(reverse('products:catalog'))
            else:
                if 'page' in ref:  # возврат на 1 страницу
                    ref = ref[:-2]
                    ref += '=1'
                    return HttpResponseRedirect(ref)
                return HttpResponseRedirect(ref)
    else:
        pass


class ProductView(ContextMixin, View):  # карточка товара (CBV)
    # template_name = 'products_app/product.html'

    current_product = None
    product_images = None
    in_basket = False
    review_form = None
    reviews = None
    review_is_exists = None
    order_delivered = None

    def post(self, *args, **kwargs):  # добавление отзыва
        self.review_form = ProductReviewForm(data=self.request.POST)
        if self.review_form.is_valid():
            instance = self.review_form.save(commit=False)
            instance.product_sku = self.kwargs['sku']
            instance.user = self.request.user
            if instance.rating:
                pass
            else:
                instance.rating = 0  # если товар не доставлен
            instance.save()
            messages.add_message(self.request, messages.INFO, 'Отзыв добавлен')

            return (HttpResponseRedirect(self.request.META['HTTP_REFERER']) if self.request.META.get(
                'HTTP_REFERER') else HttpResponseRedirect(reverse('products:catalog')))

    def get(self, *args, **kwargs):
        if all([self.kwargs['category_id'], self.kwargs['sku']]):

            try:  # объект или 404
                self.current_product = get_object_or_404(
                    getattr(products_app.models, settings.CATEGORY_ID[str(self.kwargs['category_id'])]),
                    sku=self.kwargs['sku']
                )
            except KeyError:  # если невалидная категория, то 404
                raise Http404
            else:
                self.review_form = ProductReviewForm()

                self.reviews = ProductReview.objects.select_related('user').filter(
                    product_sku=self.kwargs['sku']).order_by('-created_datetime')
                self.current_product.avg_rating = self.reviews.average_rating()  # обновляем рейтинг товара
                self.current_product.save()

                if not self.request.user.is_anonymous:  # ищем заказ, c текущим товаром, со статусом 'delivered'
                    self.review_is_exists = self.reviews.filter(user=self.request.user).exists()
                    if not self.review_is_exists:
                        delivered_orders = OrderItem.objects.select_related(
                            'order_id', 'user_id', 'product_category').filter(
                            user_id=self.request.user, product_sku=self.kwargs['sku'],
                            order_id__status='delivered').last()
                        self.order_delivered = True if delivered_orders else False

                self.product_images = ProductImage.objects.filter(sku=self.kwargs['sku'])  # ищем изображения товара

                try:  # проверяем, что артикул есть в корзине
                    session = self.request.session['basket']
                except KeyError:
                    # print('product: basket не найден')
                    pass
                else:
                    for i in session:
                        if int(i) == self.current_product.sku:
                            self.in_basket = True
                return render(self.request, 'products_app/product.html', self.get_context_data())
        else:
            return HttpResponseRedirect(reverse('index'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Store - ' + self.current_product.name
        context['current_product'] = self.current_product
        context['product_images'] = self.product_images
        context['in_basket'] = self.in_basket
        context['review_form'] = self.review_form
        context['reviews'] = self.reviews
        context['review_is_exists'] = self.review_is_exists
        context['order_delivered'] = self.order_delivered
        context['path_category'] = int(self.request.path.split('/')[3])

        return context


# def product(request, category_id=None, sku=None):  # карточка товара (заменен на CBV)
#
#     if request.method == 'POST':
#         review_form = ProductReviewForm(data=request.POST)
#         if review_form.is_valid():
#             instance = review_form.save(commit=False)
#             instance.product_sku = sku
#             instance.user = request.user
#             if instance.rating:
#                 pass
#             else:
#                 instance.rating = None  # если товар не доставлен
#             instance.save()
#             messages.add_message(request, messages.INFO, 'Отзыв добавлен')
#
#             return (HttpResponseRedirect(request.META['HTTP_REFERER']) if request.META.get(
#                 'HTTP_REFERER') else HttpResponseRedirect(reverse('index')))
#
#     if all([category_id, sku]):
#         current_product = None
#         product_images = None
#         in_basket = False
#         reviews = None
#         order_status = None
#
#         review_form = ProductReviewForm()
#
#         current_product = getattr(products_app.models, settings.CATEGORY_ID[str(category_id)]).objects.get(sku=sku)
#         reviews = ProductReview.objects.filter(product_sku=sku).order_by('-created_datetime')
#         current_product.avg_rating = reviews.average_rating()  # обновляем рейтинг товара
#         current_product.save()
#         product_images = ProductImage.objects.filter(sku=sku)
#         review_is_exists = False if request.user.is_anonymous else reviews.filter(user=request.user).exists()
#         if not review_is_exists and not request.user.is_anonymous:
#             try:
#                 current_order_id = OrderItem.objects.get(user_id=request.user, product_sku=sku).order_id.id
#             except ObjectDoesNotExist:
#                 pass
#             else:
#                 order_status = Order.objects.get(id=current_order_id).status if current_order_id else None
#
#         try:  # проверяем, что артикул есть в корзине
#             session = request.session['basket']
#         except KeyError:
#             print('product: basket не найден')
#         else:
#             for i in session:
#                 if int(i) == current_product.sku:
#                     in_basket = True
#     else:
#         return HttpResponseRedirect(reverse('index'))
#
#     context = {
#         # 'title': 'e-Store - Карточка товара',
#         'current_product': current_product,
#         'product_images': product_images,
#         'in_basket': in_basket,
#         'review_form': review_form,
#         'reviews': reviews,
#         'reviews_is_exists': review_is_exists,
#         'order_status': order_status,
#
#     }
#
#     return render(request, 'products_app/product.html', context)


class SearchView(TitleMixin, ListView):  # поиск
    template_name = 'products_app/search.html'
    title = 'e-Store - Поиск'
    QUERYSET_VALUES = ['sku', 'category', 'brand', 'name', 'short_description', 'thumbnail', 'price', 'avg_rating']

    # paginate_by = 5

    def get_queryset(self):  # поиск по названию и артикулу
        if len(self.request.GET.get('q')) > 1:
            try:
                sku = int(self.request.GET.get('q'))
            except ValueError:
                queryset = (
                    ProcessorList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES).
                    union(VideoCardList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES)).
                    union(MotherboardList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES)).
                    union(MemoryList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES))
                )
                return queryset.order_by('category', '-avg_rating', 'name')

            else:
                queryset = (
                    ProcessorList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES).
                    union(ProcessorList.objects.filter(
                        sku__icontains=sku).values(*self.QUERYSET_VALUES)
                          ).
                    union(VideoCardList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES)).
                    union(VideoCardList.objects.filter(
                        sku__icontains=sku).values(*self.QUERYSET_VALUES)
                          ).
                    union(MotherboardList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES)).
                    union(MotherboardList.objects.filter(
                        sku__icontains=sku).values(*self.QUERYSET_VALUES)
                          ).
                    union(MemoryList.objects.filter(
                        name__icontains=self.request.GET.get('q')).values(*self.QUERYSET_VALUES)).
                    union(MemoryList.objects.filter(
                        sku__icontains=sku).values(*self.QUERYSET_VALUES)
                          )
                )
                return queryset.order_by('category', '-avg_rating', 'name')

        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['query_string'] = self.request.GET.get('q')

        return context
