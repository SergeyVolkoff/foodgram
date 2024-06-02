from django.db import models

from backend.foodgram.users.models import Users


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        unique=True
    )
    slug = models.SlugField()
    color = models.CharField(
        verbose_name = 'Название',
        max_length=100,
    )


class Ingredient(models.Model):
    units_measure = models.CharField(
        max_length=150,
        verbose_name='Единицы измерения'
    )


class Recipe(models.Model):

    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name="Tags"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Text',
        help_text="Input text"
    )
    coocing_time = models.PositiveBigIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )


class RecipeIngredient(models.Model):
    """For Recipe&Ingrredient"""
    pass
