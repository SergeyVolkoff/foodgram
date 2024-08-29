from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class Users(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name='Почта',
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
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars',
        blank=True,
        null=True,
    )

    REQUIRED_FIELDS = ("first_name", "last_name", "username")
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь подписчик'
    )
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Автор рецепта'
    )
    subscription_date = models.DateTimeField(
        verbose_name='Дата подписки',
        auto_now_add=True,
        null=True
    )

    class Meta:
        ordering = ('subscription_date',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_subscription')]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
