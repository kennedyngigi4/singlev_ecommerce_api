from django.urls import path
from apps.products.views.admin_views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"features", FeatureViewSet, basename="features"),
router.register(r"categories", CategoryViewSet, basename="categories"),
router.register(r"brands", BrandViewSet, basename="brands"),
router.register(r"products", ProductViewSet, basename="products"),
urlpatterns = router.urls


urlpatterns += [
    path( "category-children/", CategoryChildrenView.as_view(), name="category-children"),
    path( "add-variant/",ProductVariantCreateView.as_view(), name="add-variant"),
]


