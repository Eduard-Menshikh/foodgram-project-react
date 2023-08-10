from django.urls import path, include
from rest_framework import routers

from api.views import (CastomUserViewSet, TagViewSet,
                       RecipeViewSet, IngredientViewSet)


router = routers.DefaultRouter()
router.register('users', CastomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
