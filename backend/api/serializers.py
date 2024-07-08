import base64
from django.core.files.base import ContentFile
from django.forms import ValidationError
from rest_framework import serializers, status

from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeTag,
                            RecipeIngredient,
                            FavoriteRecipes,
                            ShoppingByRecipe)
from users.models import Users, Subscriptions


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for Ingredient objects.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class UserSerializer(serializers.ModelSerializer):
    """
    Short presentation of User for users list.
    """
    is_subscribed = serializers.SerializerMethodField()
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Users
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'id')
        # fields = "__all__"

    def get_is_subscribed(self, obj):
        """Проверка подписки у пользователя."""
        user = self.context.get('request').user
        return (not (user.is_anonymous or user == obj)
                and user.follower.filter(following=obj).exists())


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag objects.
    """

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Ingredient.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'amount',)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'amount_min'
            )
        elif value > 10000:
            raise serializers.ValidationError(
                'amount_max'
            )
        return value


class RecipeSerializerSet(serializers.ModelSerializer):
    """
    Serializer for Post, Patch.
    """
    tag = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'does_not_exist'},
        many=True
    )
    image = Base64ImageField()
    ingredient = IngredientRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(allow_null=False, min_value=1)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tag',
                  'author',
                  'ingredient',
                  'name',
                  'text',
                  'image',
                  'cooking_time')
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        tags = data.get('tags')

        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                "Рецепт должен содержать хотя бы один тег.")

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги должны быть уникальными.")

        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    f"Тег с ID {tag.id} не был найден.")

        if not isinstance(ingredients_data, list):
            raise serializers.ValidationError(
                "Не был получен список ингредиентов.")

        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент.")

        if len(ingredients_data) != len(set(tuple(ingredient.items())
                                            for ingredient
                                            in ingredients_data)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными.")
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.get_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags', None)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
            instance.ingredients.clear()
            instance.tags.clear()
            if tags_data:
                RecipeTag.objects.bulk_create(
                    self.get_tags_list(tags_data, instance)
                )
            RecipeIngredient.objects.bulk_create(
                self.get_ingredients_list(ingredients_data, instance)
            )
            instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializerGet(instance, context=self.context).data


class RecipeSerializerGet(serializers.ModelSerializer):
    """
    Serializer for read.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('__all__',)

    def get_ingredients_recipe(self, obj):
        return obj.ingredients.values('id',
                                      'name',
                                      'units_measure',
                                      )

    def get_recipe_favorited(self, obj):
        user = self.context.get('request').user
        if user and not user.is_anonymous:
            return FavoriteRecipes.objects.filter(
                user=user,
                recipe=obj).exists()
        return False

    def get_recipe_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user and not user.is_anonymous:
            return ShoppingByRecipe.objects.filter(
                user=user,
                recipe=obj).exists()
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingByRecipe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message=('Рецепт уже добавлен!')
            )
        ]


class ShoppingByRecipeSerializer(FavoriteRecipeSerializer):
    """Purchase serializer."""

    class Meta:
        model = ShoppingByRecipe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message=('Рецепт уже добавлен!')
            )
        ]


class RecipeSerializerShort(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)
        read_only_fields = ('__all__',)


class ShowSubscriberSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user subscriptions.
    """

    recipes = RecipeSerializerShort(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = Users
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')
        read_only_fields = ('__all__',)

    def get_count_recipes(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        request = self.root.context.get('request')
        if request:
            count = request.query_params.get('recipes_limit')
        else:
            count = self.root.context.get('recipes_limit')
        if count:
            represent['recipes'] = represent['recipes'][:int(count)]
        return represent


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('user',
                  'following',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=['user', 'following'],
                message='не подписаны на автора'
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('following'):
            raise ValidationError(
                'Нельзя подписаться на себя',
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return ShowSubscriberSerializer(instance.following, context={
            'request': self.context.get('request')
        }).data
