from django.urls import path
from apps.vendor.views.views import VendoDashboardView, VendorProductsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"products", VendorProductsView, basename="products")
urlpatterns = router.urls

urlpatterns += [
    path("dashboard/", VendoDashboardView.as_view(), name="dashboard", ),
]


