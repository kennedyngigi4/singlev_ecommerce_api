from django.urls import path
from apps.manager.views import *


urlpatterns = [
    path( "stats/", StatsDashboardView.as_view(), name="stats"),
    path( "products/", AllProductsView.as_view(), name="products" ),
    path("all-orders/", AllOrdersView.as_view(), name="all-orders" ),
    path("order-details/<str:pk>/", OrderDetailsView.as_view(), name="order-details", ),
    path("dispatch-order/", DispatchOrderView.as_view(), name="dispatch-order"),
]


