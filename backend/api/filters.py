from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ['name', ]


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        lookup_expr='icontains',
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, values):
        if values and self.request.user.is_authenticated:
            return queryset.filter(recipe_favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, values):
        if values and self.request.user.is_authenticated:
            return queryset.filter(shopp_recipe__user=self.request.user)
        return queryset
    
    class Meta:
        model = Recipe
        fields = ['tags', 'author']