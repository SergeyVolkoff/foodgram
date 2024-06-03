from django.db import models

from users.models import Users


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
        through='RecipeIngredient',
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Text',
        help_text="Input text"
    )
    coocing_time = models.PositiveIntegerField(
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
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
    )


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        Users,
        related_name='favorite',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )


class ShoppingByRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopp_recipe',
        verbose_name='Список покупок',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        Users,
        verbose_name='Пользователь покупок',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )