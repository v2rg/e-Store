from django.apps import AppConfig


class BasketAppConfig(AppConfig):
    verbose_name = 'Корзина'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'basket_app'
