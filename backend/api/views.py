import random
import string
from django.db.models import Sum
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import (ListAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingByRecipe, Tag)
from users.models import Subscription, Users
from .filters import IngredientFilter, RecipeFilter
from .pagination import RecipePagination
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (AvatarSerialiser, FoodUserSerializer,
                          IngredientSerializer, RecipeSerializerGet,
                          RecipeSerializerSet, RecipeSerializerShort,
                          ShowSubscriberSerializer,
                          SubscriberSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeSerializerSet
        return RecipeSerializerGet

    @staticmethod
    def add_obj(request, pk, model):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise ValidationError(
                'Такого рецепта нет!'
            )
        user = get_object_or_404(Users, id=request.user.id)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializerShort(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_obj(request, pk, model_name):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model_name.objects.filter(user=request.user,
                                        recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'],
            detail=True,
            url_path='favorite', url_name='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """recipes/{id}/favorite/."""
        return self.add_obj(request, pk, FavoriteRecipe)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_obj(request, pk, FavoriteRecipe)

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.add_obj(request, pk, ShoppingByRecipe)

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
            recipe__recipe_shopping__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__units_measure'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_for_buy(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')

    @action(methods=['GET'],
            url_name='redirect_to_full_link',
            url_path='get-link',
            detail=True)
    def redirect_to_full_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response(
            {'short-link': url},
            status=status.HTTP_200_OK
        )


class UserViewSet(UserViewSet):
    queryset = Users.objects.all()
    serializer_class = FoodUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = RecipePagination

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

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated],
            url_name='me')
    def me(self, request, *args, **kwargs):
        serializer = FoodUserSerializer(self.request.user,
                                        context={'request': request}
                                        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                   'error': 'Вы не были подписаны!'}
        return self.delete_subscribe(Subscription, filter_set, message)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriberSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET', 'PUT'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar', url_name='avatar',)
    def addavatar(self, request):
        serializer = AvatarSerialiser(
            self.request.user,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @addavatar.mapping.delete
    def delete_avatar(self, request):
        serializer = AvatarSerialiser(
            self.request.user,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriberViewSet(ListAPIView):
    serializer_class = ShowSubscriberSerializer
    pagination_class = RecipePagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.subscriber.all()

def generate_short_url():
    url_sub = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    return "http:/localhost/s/" + url_sub
