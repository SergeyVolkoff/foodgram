import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            FavoriteRecipes,
                            ShoppingByRecipe)
from users.models import Users, Subscribe


class Base64ImageField(serializers.ImageField):
    """Конвертация base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
    
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                #   'is_subscribed',
                  'id')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeSerialazerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    # ingredients = serializers.SerializerMethodField()
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
        
    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  # 'ingredients',
                  # 'is_favorited',
                  # 'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('__all__',)

class RecipeSerializerSet(serializers.ModelSerializer):
    tag = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist':'does_not_exist'},
        many=True
    )
    image = Base64ImageField()
    # ingredients = IngredientRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(allow_null=False, min_value=1)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tag',
                  'author',
                  # 'ingredients',
                  'name',
                  'image',
                  'text',
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
        instance.image = validated_data.get('image', instance.image)
        instance.tags.clear()
        tags_list = self.initial_data.get('tags')
        instance.tags.set(tags_list)
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        ingredient_list = validated_data.pop('ingredients')
        self.get_ingredient(instance, ingredient_list)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerialazerGet(instance, context=self.context).data

class RecipeSerializerGet(serializers.ModelSerializer):
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

    def get_ingredients(self, obj):
        return obj.ingredients.values('id',
                                      'name',
                                      'measurement_unit',
                                      amount=F('recipe__amount'))

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user and not user.is_anonymous:
            return FavoriteRecipes.objects.filter(user=user, recipes=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user and not user.is_anonymous:
            return ShoppingByRecipe.objects.filter(user=user, recipes=obj).exists()
        return False