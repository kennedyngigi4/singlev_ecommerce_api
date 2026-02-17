from django.urls import path
from apps.mobile.views.views import *


urlpatterns = [
    path("home/", MobileHomeView.as_view(), name="home", ),
]

