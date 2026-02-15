from django.urls import path
from apps.orders.views.views import *


urlpatterns = [
    path( "place-order/", OrdersView.as_view(), name="place-order"),
    path( "my-orders/", MyOrdersView.as_view(), name="my-orders" ),
    path( "order/<str:pk>/", OrderDetailsView.as_view(), name="order", ),
    path( "order-payment/", OrderPayment.as_view(), name="order-payment" ),
]

