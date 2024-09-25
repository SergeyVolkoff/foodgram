from django_filters.rest_framework import (FilterSet,
                                           filters)
from recipes.models import Ingredient, Recipe, Tag
from users.models import Users


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=Users.objects.all(),
        lookup_expr='icontains'
    )
    is_favorited = filters.BooleanFilter(method='is_favorited_filter',
                                         field_name='is_favorited'
                                         )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='is_in_shopping_cart_filter')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe_favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe_shopping__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)
