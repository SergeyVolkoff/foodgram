from django.forms import ValidationError
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            # RecipeTag,
                            RecipeIngredient,
                            FavoriteRecipes,
                            ShoppingByRecipe)
from users.models import Users, Subscriptions


class IngredientSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'units_measure')
        read_only_fields = ('__all__',)


class FoodUserSerializer(UserSerializer):
    
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'id')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscriptions.objects.filter(
                author=obj, user=user).exists()
            return True
        return False
    
    def create(self, validated_data):
        return Users.objects.create_user(**validated_data)

    
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')



class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    # id = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField(source='ingredient.id')
    
    units_measure = serializers.ReadOnlyField(
        source='ingredient.units_measure')
    amount = serializers.IntegerField()

       
    @staticmethod
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество не может быть 0'
            )
        elif value > 50:
            raise serializers.ValidationError(
                'Количество не может быть > 50'
            )
        return value
    class Meta:
        model = RecipeIngredient
        fields = ( 'id', 'name', 'amount','units_measure') 


class RecipeSerializerGet(serializers.ModelSerializer):
    """
    Serializer for read.
    """
    tags = TagSerializer(many=True)
    author = FoodUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,source='ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
                user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user and not user.is_anonymous:
            return ShoppingByRecipe.objects.filter(
                user=user, recipe=obj).exists()
        return False


class CustomIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество не может быть 0'
            )
        elif value > 50:
            raise serializers.ValidationError(
                'Количество не может быть > 50'
            )
        return value

    class Meta:
        model = RecipeIngredient
        fields = ( 'id',  'amount')


class RecipeSerializerSet(serializers.ModelSerializer):
    """
    Serializer for write.
    """
  
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    ingredients = CustomIngredientRecipeSerializer(many=True)
    author = FoodUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        if not tags:
            raise serializers.ValidationError(
                "Должен быть хотя бы один тег!")

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Теги должны быть уникальными!")

        if not ingredients:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент!")
        
        if not isinstance(ingredients, list):
            raise serializers.ValidationError(
                "Не был получен список ингредиентов!")
        
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients':
                'Нужен игридиент!'})

        ingredient_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(pk=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Ингридиент не существует!')
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты не должны повторятся!')
            ingredient_list.append(ingredient)
            amount = item.get('amount')
            if amount is None or int(item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients':
                    ('Количество ингредиентов не может быть 0!')})
        data['ingredients'] = ingredients
        return data
    
    def create_ingredients(self,recipe, ingredients):
        ingredients_obj = []
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient.get('id'))
            amount = ingredient['amount']
            ingredients_obj.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=amount
                    
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients_obj)

    
    def create(self, validated_data):
        '''create recipe'''
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        cooking_time = validated_data.pop('cooking_time')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user,
                                       cooking_time=cooking_time,
                                       )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags', None)
        updated_instance = super().update(instance, validated_data)
        updated_instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=updated_instance).delete()
        self.create_ingredients(updated_instance, ingredients)
        return instance
    
    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializerGet(instance, context=self.context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipes
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже добавлен!'
            )
        ]


class ShoppingByRecipeSerializer(FavoriteRecipeSerializer):

    class Meta:
        model = ShoppingByRecipe
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже добавлен!'
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


class ShowSubscriberSerializer(serializers.Serializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()


    class Meta:
        model = Users
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSerializerShort(recipes, many=True,
                                     context=self.context).data


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = instance.author.recipes.all()
        if recipes_limit:
            recipes_limit = recipes[:int(recipes_limit)]

        user_data = UserSerializer(instance.author,
                                          context=self.context).data

        user_data['recipes'] = RecipeSerializerShort(
            recipes_limit, many=True,
            context=self.context).data
        user_data['recipes_count'] = len(user_data['recipes'])
        return user_data
