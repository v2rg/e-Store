from django.contrib import admin
from django.utils.safestring import mark_safe

# Register your models here.

from users_app.models import User, UserAddress, EmailVerification


class UserAddressInLine(admin.StackedInline):
    model = UserAddress
    verbose_name = 'Адрес пользователя'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['id', 'username', 'first_name', 'last_name', 'email']
    show_full_result_count = False

    list_filter = ['is_verified_email', 'is_staff', 'is_active']

    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'is_verified_email', 'is_active',
                    'date_joined', 'last_login', 'is_staff']

    inlines = [UserAddressInLine]

    fieldsets = (
        ('Основные', {
            'fields': ['id', 'username', 'date_joined', 'last_login', 'is_active']
        }),
        ('Данные пользователя', {
            'fields': ['first_name', 'last_name', ('email', 'is_verified_email'), 'avatar', 'avatar_preview']
        }),
        ('Статус', {
            'classes': ['collapse'],
            'fields': ['is_staff', 'is_superuser']
        }),
        ('Права', {
            'classes': ['collapse'],
            'fields': ['groups', 'user_permissions']
        }),
        # (' ', {
        #     'fields': []
        # })
    )
    filter_horizontal = ['groups', 'user_permissions']
    readonly_fields = ['id', 'username', 'date_joined', 'last_login', 'avatar_preview']

    @admin.display(description='Изображение')
    def avatar_preview(self, obj):  # превью товара
        return mark_safe(f"<img src='{obj.avatar.url}' style='max-height: 200px;'>")


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    search_fields = ['user_id__id', 'user_id__username', 'user_id__last_name', 'city']
    list_select_related = ['user_id']
    show_full_result_count = False

    list_display = ['display_user_id', 'user_id', 'city']
    ordering = ['-user_id__id']

    fields = ['user_id', 'postcode', 'city', 'street', 'building', 'floor', 'apartment']
    readonly_fields = ['user_id']

    @admin.display(description='ID пользователя')
    def display_user_id(self, obj):  # User.id вместо UserAddress.id
        return obj.user_id.id


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    search_fields = ['user__id', 'user__username']
    list_select_related = ['user']
    show_full_result_count = False

    list_display = ['display_user_id', 'user', 'created', 'expiration']
    ordering = ['expiration']

    fields = ['display_user_id', 'user', 'created', 'expiration', 'uuid_code']
    readonly_fields = ['display_user_id', 'user', 'created', 'expiration', 'uuid_code']

    @admin.display(description='ID пользователя')
    def display_user_id(self, obj):  # User.id вместо EmailVerification.id
        return obj.user.id
