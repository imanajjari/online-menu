from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import OwnerLoginView, SignUpView


app_name = "accounts"

urlpatterns = [
    path("login/", OwnerLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
]

