from django.urls import path
from apps.mobile.views.views import *
from apps.orders.views.views import *

urlpatterns = [
    path("home/", MobileHomeView.as_view(), name="home", ),
    path("categories/", MobileCategoriesView.as_view(), name="categories", ),
    path("category-tree/<str:root_id>/", MobileCategoryTreeView.as_view(), name="category-tree"),
    path("category-products/<str:category_id>/", MobileCategoryProductsView.as_view(), name="category-products"),
    path( "my-orders/", MyOrdersView.as_view(), name="my-orders" ),
]

