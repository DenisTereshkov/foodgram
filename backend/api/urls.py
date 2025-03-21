from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    FoodgramUserViewSet,
    RecipeViewSet,
    TagViewSet,
)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', FoodgramUserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
