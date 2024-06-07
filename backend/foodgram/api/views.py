from django.shortcuts import render
from rest_framework import generics, viewsets

from .serializers import (UserSerializer,
                          TagSerializer,
                          RecipeSerialazer
                          )
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            FavoriteRecipes,
                            ShoppingByRecipe)
from users.models import Users, Subscribe


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerialazer