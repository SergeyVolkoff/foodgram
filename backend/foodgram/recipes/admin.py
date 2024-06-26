from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (Tag,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     FavoriteRecipes,
                     ShoppingByRecipe)

from users.models import Subscriptions, Users



admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipes)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingByRecipe)

@admin.register(Users)
class UserAdmins(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        # 'count_follow',
        'count_recipe',
    )
    list_filter = ('username', 'email')
    search_fields = ('username',)

    def count_follow(self, obj):
        return obj.folowing.count()

    def count_recipe(self, obj):
        return obj.recipes.count()
    count_follow.short_description = 'Кол-во подписчиков'
    count_recipe.short_description = 'Кол-во рецептов'

# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'measurement_unit',
#     )
#     list_filter = ('name',)
    
@admin.register(Subscriptions)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    list_filter = ('user',)
    search_fields = ('user',)