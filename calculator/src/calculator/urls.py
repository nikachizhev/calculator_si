from django.urls import path

from calculator import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/calculate", views.api_calculate, name="api_calculate"),
    path("api/history", views.api_history, name="api_history"),
    path("api/health", views.api_health, name="api_health"),
]
