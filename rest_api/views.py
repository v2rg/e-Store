# Create your views here.
from django.http import Http404
from rest_framework import mixins
from rest_framework.decorators import api_view
from rest_framework.generics import (ListAPIView, get_object_or_404, CreateAPIView, RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from basket_app.models import Order, OrderItem
from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList
from products_app.serializers import (ProcessorSerializer, VideocardSerializer, MotherboardSerializer,
                                      MemorySerializer, IndexRandomSerializer, ProductSerializer,
                                      ProductReviewSerializer, ProductUserReviewSerializer)
from reviews_app.models import ProductReview
from users_app.models import User, UserAddress
from users_app.serializers import (UserRegistrationSerializer, UserProfileSerializer, UserAddressSerializer,
                                   UserOrdersSerializer, UserOrderSerializer)

"""API products_app"""


class TestAPIView(APIView):
    def get(self, request):
        return Response({'test': 'GET'})

    def post(self, request):
        return Response({'test': 'POST'})


@api_view(['GET'])
def index_random_api(request):  # API 8 рандомных товаров на главной (1-3 queries)
    if request.method == 'GET':
        random_processors = ProcessorList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category', 'brand',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_videocards = VideoCardList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category', 'brand',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_motherboards = MotherboardList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category', 'brand',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_memories = MemoryList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category', 'brand',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_products = random_processors.union(random_videocards).union(random_motherboards).union(random_memories)

        serializer = IndexRandomSerializer(random_products, many=True)

        return Response(serializer.data)


class IndexRandomAPIList(APIView):  # API 8 рандомных товаров на главной (1-3 queries)
    def get(self, request):
        random_processors = ProcessorList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category__category_name', 'brand__brand_name',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_videocards = VideoCardList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category__category_name', 'brand__brand_name',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_motherboards = MotherboardList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category__category_name', 'brand__brand_name',
            'name', 'short_description', 'price').order_by('?')[:2]

        random_memories = MemoryList.objects.select_related(
            'category', 'brand').values(
            'sku', 'category__category_name', 'brand__brand_name',
            'name', 'short_description', 'price').order_by('?')[:2]

        return Response(random_processors.union(random_videocards).union(random_motherboards).union(random_memories))


@api_view(['GET'])
def product_api(request, sku):  # API информация о товаре, по артикулу
    if request.method == 'GET':
        obj_list = [x.objects.filter(sku=sku).values() for x in
                    (ProcessorList, VideoCardList, MotherboardList, MemoryList) if x.objects.filter(sku=sku).exists()]
        if obj_list:
            obj = get_object_or_404(obj_list[0])
            del (obj['id'], obj['short_description'], obj['thumbnail'],
                 obj['quantity'], obj['date_added'], obj['active'])  # удаляем ненужные поля

            serializer = ProductSerializer(obj)

            return Response(serializer.data)
        else:
            raise Http404


class ProductReviewsAPIView(ListAPIView):  # API все отзывы по артикулу

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'error': 'Отзывов нет'})
        else:
            serializer = ProductReviewSerializer(queryset, many=True)
            return Response(serializer.data)

    def get_queryset(self):
        if any([x.objects.filter(sku=self.kwargs['sku']).exists() for x in
                (ProcessorList, VideoCardList, MotherboardList, MemoryList)]):
            queryset = ProductReview.objects.filter(product_sku=self.kwargs['sku'])
            return queryset
        else:
            raise Http404


class ProductUserReviewViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                               GenericViewSet):  # отзыв текущего юзера о товаре, по артикулу
    queryset = ProductReview.objects.all()
    serializer_class = ProductUserReviewSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):  # получаем отзыв о товаре
        try:
            obj = self.queryset.get(user_id=self.request.user.id, product_sku=kwargs[self.lookup_field])
        except (ProductReview.DoesNotExist, ValueError):
            raise Http404
        else:
            # serializer = ProductReviewSerializer(obj, many=False)
            serializer = self.get_serializer(obj)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):  # добавляем новый отзыв о товаре
        if any([x.objects.filter(sku=request.data['product_sku']).exists() for x in
                (ProcessorList, VideoCardList, MotherboardList, MemoryList)]) and request.user.is_authenticated:
            if ProductReview.objects.filter(product_sku=request.data['product_sku'], user=request.user):
                return Response({'error': 'Отзыв уже был добавлен'})
            else:
                review = ProductReview.objects.create(
                    product_sku=request.data['product_sku'],
                    user=request.user,
                    review=request.data['review']
                )
                serializer = self.get_serializer(review)

                return Response(serializer.data)
        else:
            return Response({'error': f'товар с sku {request.data["product_sku"]} не найден'})


class ProductReviewAddAPIView(CreateAPIView):  # API добавить отзыв о товаре
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer


class ProcessorListAPIView(ListAPIView):  # API список процессоров
    queryset = ProcessorList.objects.select_related('category', 'brand', 'line', 'socket', 'memory_type')
    serializer_class = ProcessorSerializer


class VideocardListAPIView(ListAPIView):  # API список видеокарт
    queryset = VideoCardList.objects.select_related('category', 'brand', 'gpu', 'pci_version')
    serializer_class = VideocardSerializer


class MotherboardListAPIView(ListAPIView):  # API список материнок
    queryset = MotherboardList.objects.select_related('category', 'brand', 'socket', 'form_factor', 'chipset',
                                                      'memory_type', 'pci_version')
    serializer_class = MotherboardSerializer


class MemoryListAPIView(ListAPIView):  # API список озу
    queryset = MemoryList.objects.select_related('category', 'brand', 'type')
    serializer_class = MemorySerializer


"""API user_app"""


class UserRegistrationAPI(CreateAPIView):  # API регистрация пользователя
    queryset = User
    serializer_class = UserRegistrationSerializer


class UserProfileAPI(RetrieveUpdateAPIView):  # API профиль пользователя/редактирование профиля (для авторизованных)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = User.objects.get(id=self.request.user.id)
        if not obj:
            raise Http404

        return obj


class UserAddressAPI(RetrieveUpdateAPIView):  # API профиль пользователя/редактирование профиля (для авторизованных)
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = UserAddress.objects.get(user_id=self.request.user.id)
        if not obj:
            raise Http404

        return obj


class UserOrdersAPI(ListAPIView):  # API список заказов пользователя (для авторизованных)
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user_id=self.request.user.id)

        return queryset


class UserOrderAPI(ListAPIView):  # API содержимое заказа (для авторизованных)
    serializer_class = UserOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrderItem.objects.filter(user_id=self.request.user.id, order_id=self.kwargs['order_id']).order_by(
            'product_category')
        if not queryset:
            raise Http404

        return queryset
