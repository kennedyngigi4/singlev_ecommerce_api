from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]


# Superadmin Endpoints
urlpatterns += [
    path("v1/superadmin/users/", include("apps.accounts.urls.admin_urls")),
    path("v1/superadmin/products/", include("apps.products.urls.admin_urls")),
    path("v1/superadmin/orders/", include("apps.orders.urls.admin_urls")),
    path("v1/superadmin/payments/", include("apps.payments.urls.admin_urls")),
]


urlpatterns += [
    path("v1/manager/", include("apps.manager.urls")),
]


# User Endpoints
urlpatterns += [
    path("v1/account/", include("apps.accounts.urls.urls")),
    path("v1/products/", include("apps.products.urls.urls")),
    path("v1/orders/", include("apps.orders.urls.urls")),
    path("v1/payments/", include("apps.payments.urls.urls")),
]


# Mobile Endpoints
urlpatterns += [
    path("v1/mobile/", include("apps.mobile.urls")),
]




urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





