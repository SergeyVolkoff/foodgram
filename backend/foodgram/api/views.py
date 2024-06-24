from django.db.models import Sum
from django.forms import ValidationError
from django.http import HttpResponse
from djoser  import views
from django.shortcuts import get_object_or_404, render

from requests import Response
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsAdminOrReadOnly

from .serializers import (UserSerializer,
                          TagSerializer,
                          RecipeSerializerGet,
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
    serializer_class = RecipeSerializerGet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerGet
        return RecipeSerializerSet
    
    @staticmethod
    def delete_obj(request, pk, model_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        through_obj = model_name.objects.filter(user=request.user,
                                                recipe=recipe)
        if through_obj.exists():
            through_obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_205_RESET_CONTENT)
    
    @staticmethod
    def add_obj(request, pk, serializers_name):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise ValidationError(
                'recipe_not_exist'
            )
        serializer = serializers_name(data={'recipe': recipe.id,
                                            'user': request.user.id},
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
    
    @action(detail=False,
            methods=['get', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        qw_st = RecipeIngredient.objects.filter(
            recipe__buy_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',).annotate(
                amount=Sum('amount')).order_by('ingredient__name')

        ingredient_list = 'Cписок покупок:'
        for value in qw_st:
            name = value['ingredient__name']
            measurement_unit = value['ingredient__measurement_unit']
            amount = value['amount']
            ingredient_list += f'\n{name} - {amount} {measurement_unit}'
        file = 'ingredient_list'
        response = HttpResponse(
            ingredient_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={file}.pdf'
        return response
    

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