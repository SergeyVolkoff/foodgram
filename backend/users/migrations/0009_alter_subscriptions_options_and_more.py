# Generated by Django 4.2.13 on 2024-08-26 20:49

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_users_email_alter_users_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'ordering': ('subscription_date',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.RemoveConstraint(
            model_name='subscriptions',
            name='unique_user_following',
        ),
        migrations.RemoveField(
            model_name='subscriptions',
            name='following',
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscribed', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='subscription_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата подписки'),
        ),
        migrations.AddField(
            model_name='users',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users/avatars', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь подписчик'),
        ),
        migrations.AlterField(
            model_name='users',
            name='email',
            field=models.EmailField(max_length=150, unique=True, verbose_name='Почта'),
        ),
        migrations.AlterField(
            model_name='users',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='Имя пользователя'),
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_user_subscription'),
        ),
    ]