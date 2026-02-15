from django.urls import path
from apps.products.views.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"home", HomepageFeatureListViewSet, basename="home"),
urlpatterns = router.urls

urlpatterns += [
    path( "features/", FaeturesListView.as_view(), name="features", ),
    path( "categories/", CategoryListView.as_view(), name="categories", ),
    path( "brands/", BrandListView.as_view(), name="brands", ),
    path( "<slug:slug>/", CategoryProductsView.as_view(), name="category-products", ),
    path( "<slug:category_slug>/<slug:product_slug>/", ProductByCategorySlugView.as_view(), name="product-detail-by-category" ),
]

