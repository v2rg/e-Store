import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
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


class EmailVerification(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    uuid_code = models.UUIDField(unique=True, verbose_name='Код подтверждения')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expiration = models.DateTimeField(verbose_name='Дата экспирации')

    class Meta:
        verbose_name_plural = 'Подтверждение почты'

    def __str__(self):
        return f'{self.user}'

    def send_verification_email(self):  # отправка письма со ссылкой для подтверждения почты
        send_mail(
            subject='Подтверждение аккаунта e-store',
            message=f"Подтвердите почту перейдя по ссылке http://localhost:8000/users/verify/{self.user}/{self.uuid_code}\n"
                    f"Ссылка действительна в течение 48 часов",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email]
        )


class UserAddress(models.Model):  # адрес пользователя
    user_id = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    postcode = models.CharField(max_length=10, null=True, blank=True, verbose_name='Почтовый индекс')
    city = models.CharField(max_length=64, null=True, blank=True, verbose_name='Город')
    street = models.CharField(max_length=64, null=True, blank=True, verbose_name='Улица')
    building = models.CharField(max_length=64, null=True, blank=True, verbose_name='Дом')
    floor = models.CharField(max_length=64, null=True, blank=True, verbose_name='Этаж')
    apartment = models.CharField(max_length=64, null=True, blank=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f'{self.user_id.id} | {self.user_id} | OK' if self.postcode else f'{self.user_id.id} | {self.user_id}'
