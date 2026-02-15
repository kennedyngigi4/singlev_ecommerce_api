from django.shortcuts import get_object_or_404, render

from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser

from apps.accounts.models.models import User
from apps.accounts.serializers.admin_serializers import *

class AllUsersView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().filter(is_active=True)