from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Tag, Recipe, RecipeIngredient,
                            Ingredient, Favorite, ShoppingCart)
from users.models import User, Subscribe
from foodgram.settings import DEFAULT_LIMIT


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserReadSerializer(UserSerializer):
    """[GET] Список пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.subscriber.filter(author=obj).exists()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериалайзер подписок"""

    class Meta:
        model = Subscribe
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на пользователя'
            )
        ]

    def validate(self, data):
        author = data.get('author')
        subscriber = data.get('user')
        if subscriber == author:
            raise serializers.ValidationError(
                'Нелья подписаться на самого себя'
            )
        return data


class SubscribeAuthorSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.subscriptions.filter(author=author).exists()
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, author):
        return author.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    """[GET] Список рецептов без ингредиентов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """[GET] Список избранного."""
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """[GET] Список содержимого корзины покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')


class IngredientSerializer(serializers.ModelSerializer):
    """[GET] Список ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """[GET] Список тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """[GET] Список ингредиентов с количеством для конкретного рецепта."""
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """[GET, POST, PATCH, DELETE]Чтение, создание,
    изменение, удаление рецепта."""
    author = UserReadSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return obj.favorite_recipe.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return obj.shoppingcart_recipe.filter(user=user).exists()

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError('Нужно указать минимум 1 тег.')
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return data

    def create_and_update_recipe(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=int(ingredient['amount'])
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_and_update_recipe(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_and_update_recipe(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['ingredients'] = RecipeIngredientSerializer(
            instance.recipes.all(), many=True).data
        data['tags'] = TagSerializer(instance.tags, many=True).data
        return data

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        ingredients = data.get('ingredients')
        internal_value['ingredients'] = ingredients
        tags = data.get('tags')
        internal_value['tags'] = tags
        return internal_value
