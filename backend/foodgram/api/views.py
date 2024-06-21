from djoser  import views
from django.shortcuts import get_object_or_404, render

from requests import Response
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny

from .permissions import IsAdminOrReadOnly

from .serializers import (UserSerializer,
                          TagSerializer,
                          RecipeSerialazerGet,
                          RecipeSerializerSet,
                          IngredientSerializer
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
    serializer_class = RecipeSerialazerGet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerialazerGet
        return RecipeSerializerSet
    
    @staticmethod
    def delate_obj(request, pk, model_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        through_obj = model_name.objects.filter(user=request.user,
                                                recipe=recipe)
        if through_obj.exists():
            through_obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_205_RESET_CONTENT)
    

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

class UserViewSet(views.UserViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        # if name:
        #     name = urllib.parse.unquote(name)
        #     queryset = queryset.filter(name__istartswith=name)
        return queryset