from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from foodgram import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
