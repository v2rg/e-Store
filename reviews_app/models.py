from django.db import models

# Create your models here.
from users_app.models import User


class ProductReviewQuerySet(models.QuerySet):
    def average_rating(self):  # подсчитываем средний рейтинг
        if self and sum(1 for x in self if x.rating != 0) > 0:
            avg_rating = (
                round(sum(x.rating for x in self if x.rating != 0) / sum(1 for x in self if x.rating != 0),
                      1) if len(self) > 0 else None)  # сумма рейтинга / на кол-во отзывов (с рейтингом)
        else:
            return 0

        return avg_rating


class ProductReview(models.Model):
    product_sku = models.PositiveIntegerField(db_index=True, verbose_name='Артикул')
    user = models.ForeignKey(to=User, null=True, on_delete=models.CASCADE, verbose_name='Пользователь')
    review = models.CharField(max_length=2000, verbose_name='Отзыв о товаре')
    rating = models.PositiveSmallIntegerField(default=0, verbose_name='Оценка товара')
    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата написания отзыва')

    objects = ProductReviewQuerySet.as_manager()  # делаем ProductReviewQuerySet менеджером

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):  # проверка на дубликат отзыва
        if not ProductReview.objects.filter(product_sku=self.product_sku, user=self.user).exists():
            return super().save()
        else:
            print(f'Запись уже есть в таблице ProductReview', {'sku': self.product_sku, 'user': self.user.username})

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
