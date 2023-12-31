from django.conf import settings
from django.core.mail import send_mail
from django.db import models

from products_app.models import Category
from users_app.models import User


# Create your models here.

class Order(models.Model):  # заказ
    ORDER_STATUS = [
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('shipping', 'В пути'),
        ('delivered', 'Доставлен')
    ]

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    first_name = models.CharField(max_length=64, verbose_name='Имя')
    last_name = models.CharField(max_length=64, verbose_name='Фамилия')

    postcode = models.PositiveIntegerField(help_text='Индекс может содержать только цифры', verbose_name='Индекс')
    city = models.CharField(max_length=64, verbose_name='Город')
    street = models.CharField(max_length=64, verbose_name='Улица')
    building = models.CharField(max_length=64, verbose_name='Дом')
    floor = models.CharField(max_length=64, blank=True, verbose_name='Этаж')
    apartment = models.CharField(max_length=64, blank=True, verbose_name='Квартира')

    created_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_datetime = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='created', verbose_name='Статус')
    paid = models.BooleanField(default=False, verbose_name='Заказ оплачен')

    total_quantity = models.PositiveSmallIntegerField(verbose_name='Общее кол-во. товара в заказе')
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость заказа')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        # return (
        #     f'{self.id} || '
        #     f'{self.user_id.username} || '
        #     f'Создан: {self.created_datetime.strftime("%d.%m.%Y, %H:%M:%S")} | '
        #     f'Обновлен: {self.updated_datetime.strftime("%d.%m.%Y, %H:%M:%S")} || '
        #     f'Статус: {self.status}')
        return f'{self.id}'

    def send_confirmation_email(self):
        send_mail(
            subject='Подтверждение заказа e-Store',
            message=f'<b>Заказ №{self.id} создан</b>'
                    # f'\nСтатус: {self.status}\n'
                    f'\n\nОбщая стоимость: {self.total_sum}\n'
                    f'https://localhost:8000/users/orders/',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user_id.email]
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.status != 'created':
            self.paid = True
        else:
            self.paid = False
        super().save()


class OrderItem(models.Model):  # содержимое заказа
    order_id = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name='Номер заказа')
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product_category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Категория товара')
    product_sku = models.CharField(max_length=20, verbose_name='Артикул')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена товара')

    class Meta:
        verbose_name = 'содержимое заказа'
        verbose_name_plural = 'Содержимое заказов'

    def __str__(self):
        return f'{self.order_id.id} | {self.user_id} | {self.product_sku}'

    def sku_total_price(self):
        return self.quantity * self.price

    def total_price(self):
        return sum(x.sku_total_price() for x in self.objects.all())
