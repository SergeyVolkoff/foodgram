import base64
from django.core.files.base import ContentFile
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


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#         return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'units_measure')
        read_only_fields = ('__all__',)


class FoodUserSerializer(UserSerializer):
    
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
        user = self.context.get('request').user
        return (not (user.is_anonymous or user == obj)
                and user.follower.filter(following=obj).exists())
    
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


    # def get_ingredient(self, obj):
    #     return obj.ingredients.values('id', 'name',
    #                                   'units_measure',
    #                                   )

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
    # id = serializers.ReadOnlyField(source='ingredient_id')
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    # units_measure = serializers.ReadOnlyField(
    #     source='ingredient.units_measure')
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
    # cooking_time = serializers.IntegerField(allow_null=False, min_value=1)
    author = FoodUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        # tags = data.get('tags')
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
                    'Введен не существующий ингредиент')
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients':
                    ('Значение ингредиента должно быть больше 0')})
        data['ingredients'] = ingredients
        
        return data
    
    
    def create_ingredients(self, recipe, ingredients_data):
        ingredient_objects = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredient_objects)

    def create(self, validated_data):
       
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        cooking_time = validated_data.pop('cooking_time')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user,
                                       cooking_time=cooking_time,
                                       )
        
        for element  in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient['id'].id)
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=ingredient['amount'])
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
        model = ShoppingByRecipe
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

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
    
    def to_representation(self, instance):
        recipe = RecipeSerializerShort(instance.recipe,
                                       context=self.context).data
        return recipe

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     request = self.root.context.get('request')
    #     if request is not None:
    #         count = request.query_params.get('recipes_limit')
    #     else:
    #         count = self.root.context.get('recipes_limit')
    #     if count is not None:
    #         rep['recipes'] = rep['recipes'][:int(count)]
    #     return rep


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
