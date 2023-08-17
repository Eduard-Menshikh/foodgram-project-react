from django.db.models import F, Sum
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from api.mixins import CreateDeleteMixin
from recipes.models import (
    Tag, Recipe, Ingredient, Favorite,
    ShoppingCart, RecipeIngredient)
from api.serializers import (
    TagSerializer, SubscriptionSerializer,
    RecipeCreateSerializer, ShoppingCartSerializer,
    IngredientSerializer, SubscribeAuthorSerializer,
    FavoriteSerializer, RecipeSerializer)
from api.filters import SearchIngredientFilter, RecipeFilter
from users.models import User, Subscribe
from api.permissions import IsAuthorOrAdminOrReadOnly


class CastomUserViewSet(CreateDeleteMixin, UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, AllowAny)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        if request.method == 'POST':
            return self.create_obj(
                SubscribeAuthorSerializer,
                SubscriptionSerializer,
                User,
                request,
                pk=id)
        return self.delete_obj(Subscribe, user=request.user, author__id=id)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, IsAuthorOrAdminOrReadOnly)
    filter_backends = (SearchIngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet, CreateDeleteMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_obj(FavoriteSerializer,
                                   RecipeSerializer,
                                   Recipe,
                                   request,
                                   pk)
        return self.delete_obj(Favorite, user=request.user, recipe=pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_obj(ShoppingCartSerializer,
                                   RecipeSerializer,
                                   Recipe,
                                   request,
                                   pk)
        return self.delete_obj(ShoppingCart, user=request.user, recipe=pk)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        shopping_cart_recipes = (ShoppingCart.objects.
                                 filter(user=request.user).
                                 values_list('recipe', flat=True))
        ingredients = (RecipeIngredient.objects
                       .filter(recipe__in=shopping_cart_recipes)
                       .values(name=F('ingredient__name'),
                               unit=F('ingredient__measurement_unit'))
                       .annotate(amount_sum=Sum('amount'))
                       ).order_by('name')
        shopping_cart = '\n'.join([
            f'{ingredient["name"]} - {ingredient["unit"]} '
            f'{ingredient["amount_sum"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping-cart.txt"')
        response.write(shopping_cart)
        return response
