from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
class Subscribe(models.Model):
    subscribing_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscribitions',
        verbose_name='Подписчик'
    )
    user_to_subscribe = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

