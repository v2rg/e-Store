from django.contrib import admin
from django.db.models import Sum
from django.utils.safestring import mark_safe

# Register your models here.
from products_app.models import (Category, Brand, Socket, MemoryType, GpuPciVersion, GpuModel, CpuLine, MbChipset,
                                 MbFormFactor, ProductImage, ProcessorList, VideoCardList, MotherboardList, MemoryList)

COMMON_DISPLAY = ['id', 'sku', 'brand', 'name', 'price', 'quantity', 'avg_rating', 'active', 'date_added']
COMMON_FIELDS = ['sku', 'category', 'brand', 'name', 'description', 'short_description', 'thumbnail',
                 'thumbnail_preview', 'price', ('quantity', 'active'), 'avg_rating', 'date_added']


class ZeroQuantityListFilter(admin.SimpleListFilter):  # фильтр товаров по кол-ву
    title = 'Остаток товара'
    parameter_name = 'quantity'

    def lookups(self, request, model_admin):
        return (
            ('<10', 'Менее 10'),
            ('0', 'Отсутствует')
        )

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(quantity__lt=10, quantity__gt=0)
        if self.value() == '0':
            return queryset.filter(quantity=0)


class LowRatingListFilter(admin.SimpleListFilter):  # фильтр товаров по рейтингу
    title = 'Рейтинг товара'
    parameter_name = 'avg_rating'

    def lookups(self, request, model_admin):
        return (
            ('>4', 'Более 4'),
            ('<4', 'Менее 4'),
            ('0', 'Без рейтинга')
        )

    def queryset(self, request, queryset):
        if self.value() == '>4':
            return queryset.filter(avg_rating__gt=4)
        if self.value() == '<4':
            return queryset.filter(avg_rating__lt=4, avg_rating__gt=1)
        if self.value() == '0':
            return queryset.filter(avg_rating=0)


class AbstractCatalogModelAdmin(admin.ModelAdmin):  # действия для выбранных объектов (queryset)
    actions = ['make_active', 'make_not_active']
    search_fields = ['sku', 'brand__brand_name', 'name', 'price']
    show_full_result_count = False

    list_filter = ['active', ('brand', admin.RelatedOnlyFieldListFilter), ZeroQuantityListFilter, LowRatingListFilter]

    list_display = COMMON_DISPLAY
    list_display_links = ['sku']
    readonly_fields = ['date_added', 'thumbnail_preview']

    ordering = ['-date_added']

    @admin.display(description='Изображение')
    def thumbnail_preview(self, obj):  # превью товара
        return mark_safe(f"<img src='{obj.thumbnail.url}' style='max-height: 200px;'>")

    @admin.action(description='Изменить статус на Активно')
    def make_active(self, request, queryset):  # изменение статуса на Активно
        queryset.update(active=True)

    @admin.action(description='Изменить статус на НЕактивно')
    def make_not_active(self, request, queryset):  # изменение статуса на НЕактивно
        queryset.update(active=False)


@admin.register(ProcessorList)
class ProcessorListAdmin(AbstractCatalogModelAdmin):  # список процессоров
    fieldsets = (
        ('Основные', {
            'fields': COMMON_FIELDS
        }),
        ('Параметры процессора', {
            'fields': ['line', 'socket', 'cores', ('base_frequency', 'max_frequency'), 'memory_type', 'tdp']
        })
    )


@admin.register(VideoCardList)
class VideoCardListAdmin(AbstractCatalogModelAdmin):  # список видеокарт
    fieldsets = (
        ('Основные', {
            'fields': COMMON_FIELDS
        }),
        ('Параметры видеокарты', {
            'fields': [('gpu', 'gpu_frequency'), ('memory_size', 'memory_frequency'), 'pci_version', 'length']
        })
    )


@admin.register(MotherboardList)
class MotherboardListAdmin(AbstractCatalogModelAdmin):  # список мат. плат
    fieldsets = (
        ('Основные', {
            'fields': COMMON_FIELDS
        }),
        ('Параметры материнской платы', {
            'fields': ['socket', 'form_factor', 'chipset', ('memory_type', 'memory_slots'), 'pci_version']
        })
    )


@admin.register(MemoryList)
class MemoryListAdmin(AbstractCatalogModelAdmin):  # список ОЗУ
    fieldsets = (
        ('Основные', {
            'fields': COMMON_FIELDS
        }),
        ('Параметры оперативной памяти', {
            'fields': ['type', 'size', 'frequency']
        })
    )


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Socket)
admin.site.register(MemoryType)
admin.site.register(GpuPciVersion)
admin.site.register(GpuModel)
admin.site.register(CpuLine)
admin.site.register(MbChipset)
admin.site.register(MbFormFactor)

admin.site.register(ProductImage)
