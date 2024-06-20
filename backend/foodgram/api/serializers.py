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
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist':'does_not_exist'},
        many=True
    )
    image = Base64ImageField()
    # ingredients = IngredientRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  # 'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('author',)