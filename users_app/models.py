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
