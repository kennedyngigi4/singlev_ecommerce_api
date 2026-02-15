from django.urls import path
from apps.orders.views.admin_views import *


urlpatterns = [
    path("stats/", AdminDashboardStatsView.as_view(), name="stats", ),

    path("all-orders/", AllOrdersView.as_view(), name="all-orders"),
]