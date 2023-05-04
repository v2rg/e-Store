from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):  # расширение для модели User
    avatar = models.ImageField(upload_to='media/users_avatar', null=True, blank=True, verbose_name='Аватар')
    is_verified_email = models.BooleanField(default=False, verbose_name='Почта подтверждена')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
