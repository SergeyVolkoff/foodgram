import rest_framework.permissions

from django.db.models import Sum
from django.forms import ValidationError
from django.http import HttpResponse
from djoser import views
from django.shortcuts import get_object_or_404

from requests import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .pagination import DefaultPagination

from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

from .serializers import (TagSerializer,
                          RecipeSerializerGet,
                          RecipeSerializerSet,
                          IngredientSerializer,
                          ShoppingByRecipeSerializer,
                          ShowSubscriberSerializer,
                          SubscriberSerializer,
                          FavoriteRecipeSerializer,
                          CustomUserCreateSerializer
                          )
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            FavoriteRecipes,
                            ShoppingByRecipe)
from users.models import Users


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerGet
    pagination_class = DefaultPagination
    permission_classes = (IsOwnerOrReadOnly,)

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
        return Response(status=status.HTTP_400_BAD_REQUEST)

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

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """recipe/{id}/shopping_cart."""
        return self.add_obj(request, pk, ShoppingByRecipeSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_obj(request, pk, ShoppingByRecipe)

    @action(detail=False,
            methods=['get', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        data_req = RecipeIngredient.objects.filter(
            recipe__buy_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',).annotate(
                amount=Sum('amount')).order_by('ingredient__name')
        ingredient_list = 'Cписок покупок:'
        for value in data_req:
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

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """recipe/{id}/favorite/."""
        return self.add_obj(request, pk, FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_obj(request, pk, FavoriteRecipes)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class UserViewSet(views.UserViewSet):

    def get_permissions(self):
        if self.action == 'retrieve':
            return (rest_framework.permissions.AllowAny(),)
        return super().get_permissions()


    @action(detail=False,
            pagination_class=DefaultPagination,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """users/subscriptions/."""
        user = request.user
        folowing = Users.objects.filter(following__user=user)
        pages = self.paginate_queryset(folowing)
        serializer = ShowSubscriberSerializer(
            pages,
            context={
                'recipes_limit': request.query_params.get('recipes_limit')
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'],
            detail=True,
            pagination_class=DefaultPagination,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """users/{id}/subscribe/."""
        following = get_object_or_404(Users, pk=id)
        serializer = SubscriberSerializer(
            data={'user': request.user.id, 'following': following.id},
            context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit')
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        # name = self.request.query_params.get('name')
        # if name:
        #     name = urllib.parse.unquote(name)
        #     queryset = queryset.filter(name__istartswith=name)
        return queryset
