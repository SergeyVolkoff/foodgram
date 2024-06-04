from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipesViewSet,
                    )

router = DefaultRouter()
router.register(r'recipes', RecipesViewSet,basename='recipes')



urlpatterns = [
    path('', include(router.urls)),
]