from django.db import models

# Create your models here.
from users_app.models import User


class ProductReviewQuerySet(models.QuerySet):
    def average_rating(self):  # подсчитываем средний рейтинг
        return round(sum(x.rating for x in self) / len(self), 1)


class ProductReview(models.Model):
    product_sku = models.PositiveIntegerField(db_index=True, verbose_name='Артикул')
    user = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, verbose_name='Пользователь')
    review = models.CharField(max_length=2000, verbose_name='Отзыв о товаре')
    rating = models.PositiveSmallIntegerField(blank=True, verbose_name='Оценка товара')

    objects = ProductReviewQuerySet.as_manager()  # делаем ProductReviewQuerySet менеджером

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.product_sku} | {self.user} | {self.review[:50]}'
