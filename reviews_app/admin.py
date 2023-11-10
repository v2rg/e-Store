from django.contrib import admin

# Register your models here.
from reviews_app.models import ProductReview


class RatingGreaterThenZeroListFilter(admin.SimpleListFilter):
    title = 'Рейтинг'
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return (
            ('>0', 'Более 0'),
        )

    def queryset(self, request, queryset):
        if self.value() == '>0':
            return queryset.filter(rating__gt=0)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    search_fields = ['product_sku', 'user__username']
    list_select_related = ['user']
    show_full_result_count = False

    list_filter = [RatingGreaterThenZeroListFilter]

    list_display = ['id', 'product_sku', 'user', 'rating', 'created_datetime']
    ordering = ['-created_datetime']

    fields = ['id', 'user', 'product_sku', 'created_datetime', 'rating', 'review']
    readonly_fields = ['id', 'user', 'product_sku', 'created_datetime', 'rating', 'review']
