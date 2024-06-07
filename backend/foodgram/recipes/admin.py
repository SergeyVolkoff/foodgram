from django.contrib import admin

from .models import (Tag,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     FavoriteRecipes,
                     ShoppingByRecipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipes)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingByRecipe)
