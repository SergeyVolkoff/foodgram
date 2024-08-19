from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class Users(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        max_length=150,
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

    REQUIRED_FIELDS = ("first_name", "last_name", "username")
    USERNAME_FIELD = "email"

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):

    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

        def __str__(self):
            return f'{self.user} {self.following}'
