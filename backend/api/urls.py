from django.urls import include, path
from rest_framework import routers


from .views import (RecipesViewSet,
                    UserViewSet,
                    TagViewSet,
                    IngredientViewSet
                    )

router = routers.DefaultRouter()
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingridients', IngredientViewSet, basename='ingridients')


urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
