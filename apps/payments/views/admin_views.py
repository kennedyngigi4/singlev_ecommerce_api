from django.shortcuts import render


from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.payments.models import *
from apps.payments.serializers.admin_serializers import *


class AdminMpesaPaymentsView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = MpesaPaymentsSerializer
    queryset = MpesaPayment.objects.all().order_by("created_at")

