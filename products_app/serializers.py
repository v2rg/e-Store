from django.core.cache import cache
from rest_framework import serializers

from products_app.models import (ProcessorList, VideoCardList, MotherboardList, MemoryList, Category, Brand, Socket,
                                 CpuLine, MemoryType, GpuModel, GpuPciVersion, MbFormFactor, MbChipset)
from reviews_app.models import ProductReview

COMMON_FIELDS = ['sku', 'category', 'brand',
                 'name', 'description', 'price',
                 'avg_rating']
CATEGORY = serializers.SlugRelatedField(slug_field='category_name', read_only=True)
BRAND = serializers.SlugRelatedField(slug_field='brand_name', read_only=True)


class IndexRandomSerializer(serializers.Serializer):  # API 8 рандомных товаров на главной (1-3 queries)
    sku = serializers.ReadOnlyField()
    category = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    short_description = serializers.ReadOnlyField()
    price = serializers.ReadOnlyField()

    def get_category(self, obj):  # меняем id (FK) на category_name
        while not cache.get('categories_for_api'):
            cache.set('categories_for_api', list(Category.objects.values()), 60)  # кэшируем таблицу Category
        else:
            for i in cache.get('categories_for_api'):
                if i['id'] == obj['category']:
                    return i['category_name']
        # return Category.objects.get(id=obj['category']).category_name

    def get_brand(self, obj):  # меняем id (FK) на brand_name
        while not cache.get('brands_for_api'):
            cache.set('brands_for_api', list(Brand.objects.values()), 60)  # кэшируем таблицу Brand
        else:
            for i in cache.get('brands_for_api'):
                if i['id'] == obj['brand']:
                    return i['brand_name']
        # return Brand.objects.get(id=obj['brand']).brand_name


class ProductSerializer(serializers.BaseSerializer):  # API вывод товара по sku (поиск по 4 таблицам)
    def to_representation(self, instance):  # формируем словарь под категорию товара
        data = {
            'sku': instance['sku'],
            'category': Category.objects.get(id=instance['category_id']).category_name,
            'brand': Brand.objects.get(id=instance['brand_id']).brand_name,
            'name': instance['name'],
            'description': instance['description'],
            'price': instance['price'],
            'avg_rating': instance['avg_rating']
        }  # общие поля

        if instance['category_id'] == 1:  # процессор
            data.update(
                line=CpuLine.objects.get(id=instance['line_id']).line_name,
                socket=Socket.objects.get(id=instance['socket_id']).socket_name,
                cores=instance['cores'],
                base_frequency=instance['base_frequency'],
                max_frequency=instance['max_frequency'],
                memory_type=MemoryType.objects.get(id=instance['memory_type_id']).type_name,
                tdp=instance['tdp']
            )
        elif instance['category_id'] == 2:  # видеокарта
            data.update(
                gpu=GpuModel.objects.get(id=instance['gpu_id']).gpu_name,
                gpu_frequency=instance['gpu_frequency'],
                memory_size=instance['memory_size'],
                memory_frequency=instance['memory_frequency'],
                pci_version=GpuPciVersion.objects.get(id=instance['pci_version_id']).version_name,
                length=instance['length']
            )
        elif instance['category_id'] == 3:  # материнская плата
            data.update(
                socket=Socket.objects.get(id=instance['socket_id']).socket_name,
                form_factor=MbFormFactor.objects.get(id=instance['form_factor_id']).formfactor_name,
                chipset=MbChipset.objects.get(id=instance['chipset_id']).chipset_name,
                memory_type=MemoryType.objects.get(id=instance['memory_type_id']).type_name,
                memory_slots=instance['memory_slots'],
                pci_version=GpuPciVersion.objects.get(id=instance['pci_version_id']).version_name
            )
        elif instance['category_id'] == 4:  # память
            data.update(
                type_id=MemoryType.objects.get(id=instance['memory_type_id']).type_name,
                size=instance['size'],
                frequency=instance['frequency']
            )

        return data


class ProductReviewSerializer(serializers.ModelSerializer):  # API отзывы по артикулу
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['product_sku', 'user', 'rating', 'created_datetime', 'review']


class ProductUserReviewSerializer(serializers.ModelSerializer):  # API отзыв пользователя по артикулу
    class Meta:
        model = ProductReview
        fields = ['product_sku', 'created_datetime', 'review']


class ProcessorSerializer(serializers.ModelSerializer):  # API список всех процессоров
    category = CATEGORY
    brand = BRAND
    line = serializers.SlugRelatedField(slug_field='line_name', read_only=True)
    socket = serializers.SlugRelatedField(slug_field='socket_name', read_only=True)
    memory_type = serializers.SlugRelatedField(slug_field='type_name', read_only=True)

    class Meta:
        model = ProcessorList
        fields = COMMON_FIELDS + [
            'line', 'socket', 'cores',
            'base_frequency', 'max_frequency', 'memory_type',
            'tdp'
        ]


class VideocardSerializer(serializers.ModelSerializer):  # API список всех видеокарт
    category = CATEGORY
    brand = BRAND
    gpu = serializers.SlugRelatedField(slug_field='gpu_name', read_only=True)
    pci_version = serializers.SlugRelatedField(slug_field='version_name', read_only=True)

    class Meta:
        model = VideoCardList
        fields = COMMON_FIELDS + [
            'gpu', 'gpu_frequency', 'memory_size',
            'memory_frequency', 'pci_version', 'length'
        ]


class MotherboardSerializer(serializers.ModelSerializer):  # API список всех материнок
    category = CATEGORY
    brand = BRAND
    socket = serializers.SlugRelatedField(slug_field='socket_name', read_only=True)
    form_factor = serializers.SlugRelatedField(slug_field='formfactor_name', read_only=True)
    chipset = serializers.SlugRelatedField(slug_field='chipset_name', read_only=True)
    memory_type = serializers.SlugRelatedField(slug_field='type_name', read_only=True)
    pci_version = serializers.SlugRelatedField(slug_field='version_name', read_only=True)

    class Meta:
        model = MotherboardList
        fields = COMMON_FIELDS + [
            'socket', 'form_factor', 'chipset',
            'memory_type', 'memory_slots', 'pci_version'
        ]


class MemorySerializer(serializers.ModelSerializer):  # API список всех ОЗУ
    category = CATEGORY
    brand = BRAND
    type = serializers.SlugRelatedField(slug_field='type_name', read_only=True)

    class Meta:
        model = MemoryList
        fields = COMMON_FIELDS + [
            'type', 'size', 'frequency'
        ]
