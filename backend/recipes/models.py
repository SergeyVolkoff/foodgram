from django.db import models
from django.core.validators import MinValueValidator

from users.models import Users


class Tag(models.Model):

    name = models.CharField(
        verbose_name='Название',
        max_length=32,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=32,
        verbose_name='Уникальный слаг',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name='Название',
        max_length=128,
    )
    units_measure = models.CharField(
        max_length=64,
        verbose_name='Единицы измерения'
    )

    class Meta:
        # ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Список id тегов",
        related_name='recipe_as_tag',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='RecipeIngredient',
        related_name='recipe_as_ingredients'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Текст',
        help_text='Введите текст',
        # verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления(в минутах)',
        help_text='Введите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    '''Bridging model!'''
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[
            MinValueValidator(
                1, message='Ингредиентов не может быть меньше 1')]
    )

    class Meta:
        verbose_name = 'Кол-во ингридиента в рецепте'
        verbose_name_plural = 'Кол-во ингридиента в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Уникальное значение')]

    def __str__(self):
        return f'{self.ingredient}–{self.amount}'


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

    class Meta:
        verbose_name = 'Рецепт для покупок'
        verbose_name_plural = 'Рецепты для покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


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
