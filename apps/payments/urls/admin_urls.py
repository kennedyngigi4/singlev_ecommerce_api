from django.urls import path
from apps.payments.views.admin_views import *


urlpatterns = [
    path("mpesa/", AdminMpesaPaymentsView.as_view(), name="mpesa" ),
]

