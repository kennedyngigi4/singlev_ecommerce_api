from django.urls import path
from apps.accounts.views.views import *


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register" ),
    path("login/", LoginView.as_view(), name="login" ),

    path("me/", UserProfile.as_view(), name="me" ),
    path("password-reset/", PasswordResetRequestView.as_view()),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view()),
]

