from django.urls import path
from apps.payments.views.views import *


urlpatterns = [
    path("callback/", callbackView, name="callback" )
]


