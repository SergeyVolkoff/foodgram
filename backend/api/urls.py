from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, SubscriberViewSet,
                    TagViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('users/subscriptions/', SubscriberViewSet.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
