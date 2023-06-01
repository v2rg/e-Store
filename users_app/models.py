from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

def user_directory_path(instance, image):
    return f'users_avatars/{instance.id}/{image}'


class User(AbstractUser):  # расширение для модели User
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True, verbose_name='Аватар')
    is_verified_email = models.BooleanField(default=False, verbose_name='Почта подтверждена')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'


class UserAddress(models.Model):  # адрес пользователя
    user_id = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    postcode = models.PositiveIntegerField(null=True, blank=True, verbose_name='Почтовый индекс')
    city = models.CharField(max_length=64, null=True, blank=True, verbose_name='Город')
    street = models.CharField(max_length=64, null=True, blank=True, verbose_name='Улица')
    building = models.CharField(max_length=10, null=True, blank=True, verbose_name='Дом')
    floor = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Этаж')
    apartment = models.CharField(max_length=10, null=True, blank=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f'{self.user_id.id} | {self.user_id} | OK' if self.postcode else f'{self.user_id.id} | {self.user_id}'
