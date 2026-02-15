from django.urls import path
from apps.accounts.views.admin_views import *

urlpatterns = [
    path("all/", AllUsersView.as_view(), name="all" ),
]


