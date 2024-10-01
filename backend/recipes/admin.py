from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            FavoriteRecipe,
                            ShoppingByRecipe)
from users.models import Subscription, Users


class UsersAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
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


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'units_measure',
    )
    search_fields = ('name',)
    list_filter = ('units_measure',)
    list_display_links = ('name',)
    empty_value_display = 'Empty'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
    )

    list_filter = ('tags',)
    search_fields = ('name', 'author', 'pub_date' )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Subscription)
admin.site.register(Users, UserAdmin)
