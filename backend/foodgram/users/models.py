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
    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    
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
    class Meta:

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['subscribing_user', 'user_to_subscribe'],
        #         name='unique_subscribe'
        #     )
        # ]
        def __str__(self):
            return f'{self.user} {self.following}'
