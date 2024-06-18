from djoser  import views
from django.shortcuts import render

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from .serializers import (UserSerializer,
                          TagSerializer,
                          RecipeSerialazerGet,
                          RecipeSerializerSet
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
    # serializer_class = RecipeSerialazerGet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerialazerGet
        return RecipeSerializerSet


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

class UserViewSet(views.UserViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    