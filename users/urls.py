from django.urls import path, include
from .views import register

urlpatterns = [
    path("register/", register, name="register"),
    path("", include("django.contrib.auth.urls")), # login, logout, password_change, etc.
]
