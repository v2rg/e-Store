from django.db import models

# Create your models here.
from users_app.models import User


class ProductReviewQuerySet(models.QuerySet):
    def average_rating(self):  # подсчитываем средний рейтинг
        if self and sum(1 for x in self if x.rating is not None) > 0:
            avg_rating = (round(
                sum(x.rating for x in self if x.rating is not None) / sum(1 for x in self if x.rating is not 0),
                1) if len(self) > 0 else None)  # сумма рейтинга / на кол-во отзывов (с рейтингом)
        else:
            avg_rating = None

        return avg_rating


class ProductReview(models.Model):
    product_sku = models.PositiveIntegerField(db_index=True, verbose_name='Артикул')
    user = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, verbose_name='Пользователь')
    review = models.CharField(max_length=2000, verbose_name='Отзыв о товаре')
    rating = models.PositiveSmallIntegerField(null=True, verbose_name='Оценка товара')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата написания отзыва')

    objects = ProductReviewQuerySet.as_manager()  # делаем ProductReviewQuerySet менеджером

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        # return f'{self.product_sku} | {self.user} | {self.review[:50]}'
        return f'{self.product_sku}'

    def iter_range(self):  # для вывода рейтинга в виде звезд
        return range(self.rating)


# class AvgReview(models.Model):
#     product_sku = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
#     avg_review = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='Средний рейтинг')
#
#     def __str__(self):
#         return f'{self.product_sku} | {self.avg_review}'
