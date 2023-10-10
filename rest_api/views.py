# Create your views here.

from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, get_object_or_404, CreateAPIView, RetrieveUpdateAPIView, \
    RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from basket_app.models import Order, OrderItem
from products_app.models import ProcessorList, VideoCardList, MotherboardList, MemoryList
from products_app.serializers import (ProcessorSerializer, VideocardSerializer, MotherboardSerializer,
                                      MemorySerializer, IndexRandomSerializer, ProductSerializer)
from reviews_app.models import ProductReview
from users_app.models import User, UserAddress
from users_app.serializers import UserRegistrationSerializer, UserProfileSerializer, UserAddressSerializer, \
    UserOrdersSerializer, UserOrderSerializer

"""API products_app"""


class TestAPIView(APIView):
    def get(self, request):
        return Response({'test_get': 'test'})

    def post(self, request):  # добавить отзыв к товару (user: test)
        if (ProcessorList.objects.filter(sku=request.data['product_sku']) or
                VideoCardList.objects.filter(sku=request.data['product_sku']) or
                MotherboardList.objects.filter(sku=request.data['product_sku']) or
                MemoryList.objects.filter(sku=request.data['product_sku'])):

            test_user = User.objects.get(username='test')
            current_review = ProductReview.objects.create(
                product_sku=request.data['product_sku'],
                user=test_user,
                review=request.data['review']
            )
            response = ProductReview.objects.filter(product_sku=request.data['product_sku'], user=test_user).values(
                'product_sku', 'review')

            return Response(response)
        else:
            return Response(f"Товара с sku {request.data['product_sku']} нет")


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

        print(random_products)

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
def product_api(request, sku):  # API товар по артикулу
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
        queryset = User.objects.get(id=self.request.user.id)
        if not queryset:
            raise Http404

        return queryset


class UserAddressAPI(RetrieveUpdateAPIView):  # API профиль пользователя/редактирование профиля (для авторизованных)
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = UserAddress.objects.get(user_id=self.request.user.id)
        if not obj:
            raise Http404

        return obj


class UserOrdersAPI(ListAPIView):  # API список заказов пользователя
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user_id=self.request.user.id)

        return queryset


class UserOrderAPI(ListAPIView):  # API содержимое заказа
    serializer_class = UserOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrderItem.objects.filter(user_id=self.request.user.id, order_id=self.kwargs['order_id']).order_by(
            'product_category')
        if not queryset:
            raise Http404

        return queryset
