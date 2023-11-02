from django.apps import AppConfig


class CommentsAppConfig(AppConfig):
    verbose_name = 'Отзывы о товарах'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews_app'
