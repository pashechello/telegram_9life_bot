from django.urls import path
from botapp import views

urlpatterns = [
    path('test/', views.test_view, name='test'),
    # Добавьте другие URL-шаблоны вашего приложения здесь
]