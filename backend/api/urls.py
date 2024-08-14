from django.urls import include, path, re_path
from rest_framework import routers
from djoser import views as djoser_views

from .views import (RecipeViewSet,
                    UserViewSet,
                    TagViewSet,
                    IngredientViewSet
                    )

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    
]
