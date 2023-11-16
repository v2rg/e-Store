from django.contrib import admin

# Register your models here.

from basket_app.models import Order, OrderItem


class OrderItemInLine(admin.StackedInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['user_id']
    verbose_name_plural = 'Содержимое заказа'
    fields = ['order_id', 'product_sku', 'quantity', 'price']

    # readonly_fields = ['order_id', 'user_id', 'product_category', 'product_sku', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['id', 'user_id__username', 'city', 'created_datetime']
    list_select_related = ['user_id']
    show_full_result_count = False

    list_filter = ['paid', 'status', 'city']

    list_display = ['id', 'user_id', 'first_name', 'last_name', 'city', 'created_datetime', 'updated_datetime',
                    'status', 'paid', 'comment']

    ordering = ['-created_datetime']

    inlines = [OrderItemInLine]
    readonly_fields = ['created_datetime', 'updated_datetime', 'user_id', 'comment', 'total_quantity', 'total_sum']
    fieldsets = (
        ('Данные заказа', {
            'fields': [('status', 'paid'), 'created_datetime', 'updated_datetime', 'total_quantity', 'total_sum', 'comment']
        }),
        ('Пользователь', {
            'fields': ['user_id', 'first_name', 'last_name']
        }),
        ('Адрес доставки', {
            'fields': ['postcode', 'city', 'street', 'building', 'floor', 'apartment']
        })
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    search_fields = ['order_id__id', 'user_id__username', 'product_sku']
    list_select_related = ['user_id', 'order_id']
    show_full_result_count = False

    list_display = ['order_id', 'user_id', 'product_sku', 'product_category', 'quantity', 'price']

    fields = ['order_id', 'user_id', 'product_sku', 'product_category', 'quantity', 'price']
    readonly_fields = ['order_id', 'user_id', 'product_sku', 'product_category']

    ordering = ['-order_id', 'product_sku']
