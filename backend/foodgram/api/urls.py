from django.urls import include, path
from rest_framework import routers


from .views import (RecipesViewSet,
                    UserViewSet,
                    TagViewSet,
                    
                    )

router = routers.DefaultRouter()
router.register(r'recipes', RecipesViewSet,basename='recipes')
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
]