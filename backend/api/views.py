import base64
import rest_framework.permissions

from django.core.files.base import ContentFile
from django.db.models import Sum
from django.forms import ValidationError
from django.http import Http404, HttpResponse
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
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
                          FoodUserSerializer,
                          RecipeSerializerShort
                          )
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            FavoriteRecipe,
                            ShoppingByRecipe)
from users.models import Users,Subscription


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerGet
    pagination_class = DefaultPagination
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return  RecipeSerializerSet
        return RecipeSerializerGet
    

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """recipe/{id}/favorite/."""
        return self.add_obj(request, pk,  FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_obj(request, pk, FavoriteRecipe)

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
                'Такого рецепта нет!'
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
        return self.add_obj(request, pk, ShoppingByRecipeSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_obj(request, pk, ShoppingByRecipe)
    
    @staticmethod
    def ingredients_for_buy(ingredients):
        shopping_list = ''
        for item in ingredients:
            shopping_list += (
                f"{item['ingredient__name']}  - "
                f"{item['sum']}"
                f"({item['ingredient__units_measure']})\n"
            )
        return shopping_list
    
    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated, ],
            url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopp_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__units_measure'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_for_buy(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')


class UserViewSet(UserViewSet):
    queryset = Users.objects.all()
    serializer_class = FoodUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination

    def add_subscribe(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete_subscribe(self, model, filter_set, message: dict):
        subscription = model.objects.filter(**filter_set).first()
        if subscription:
            subscription.delete()
            return Response({'success': message['success']},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'message': message['error']},
            status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(detail=True,
            methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        data = {'user': request.user.id, 'author': self.get_object().id}
        return self.add_subscribe(
            SubscriberSerializer(data=data, context={'request': request}))

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        filter_set = {'user': request.user, 'author': self.get_object()}
        message = {'success': 'Подписка успешно удалена!',
                   'error': 'Вы небыли подписаны!'}
        return self.delete_subscribe(Subscription, filter_set, message)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)

        paginator = self.pagination_class()
        pages  = paginator.paginate_queryset(subscriptions, request)

        serializer = SubscriberSerializer(pages, 
                                        context={'request': request},
                                        many=True
                                        )
        return paginator.get_paginated_response(serializer.data)
