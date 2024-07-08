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
    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
    )
    units_measure = models.CharField(
        max_length=150,
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
        max_length=100,
        unique=True
    )

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
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )
    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    '''Bridging model!'''
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
    class Meta:
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            )
        ]

    
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
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['recipe', 'user'],
        #         name='unique_user_recipe_in_favorites'
        #     )
        # ]


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
    
class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags_recipes'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_tags'
            )
        ]