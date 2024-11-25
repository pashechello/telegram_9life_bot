#urls.py 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from botapp.views import test_view  # Исправьте импорт

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view, name='test'),  # Добавьте эту строку
    path('', include('botapp.urls')),  # Добавьте эту строку
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns