from django.shortcuts import get_object_or_404, render

from decimal import Decimal

from django.db.models import Sum, Count
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser


from apps.accounts.models.models import *
from apps.orders.models import *
from apps.products.models.models import *
from apps.payments.models import *
from apps.orders.serializers.admin_serializers import *



class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        labels = []
        latest_orders_data = []
        latest_payments_data = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)


        orders_qs = (
            Order.objects
            .filter(date_created__range=(start_date, end_date))
            .annotate(day=TruncDate("date_created"))
            .values("day")
            .annotate(total_orders=Count("id"))
            .order_by("day")
        )

        orders_map = {o["day"]: o["total_orders"] for o in orders_qs}

        payments_qs = (
            MpesaPayment.objects
            .filter(status="paid", created_at__range=(start_date, end_date))
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total_amount=Coalesce(Sum("amount"), Decimal("0.00")))
            .order_by("day")
        )

        payments_map = {p["day"]: p["total_amount"] for p in payments_qs}
        

        current_day = start_date.date()

        while current_day <= end_date.date():
            labels.append(current_day.strftime("%Y-%m-%d"))
            latest_orders_data.append(orders_map.get(current_day, 0))
            latest_payments_data.append(float(payments_map.get(current_day, 0)))
            current_day += timedelta(days=1)

        users_count = User.objects.count()
        products_count = ProductVariant.objects.count()
        orders_count = Order.objects.count()

        total_sales = MpesaPayment.objects.filter(status="paid").aggregate(
            total_amount=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total_amount"]

        response = {
            "users_count": users_count,
            "orders_count": orders_count,
            "products_count": products_count,
            "total_sales": total_sales,
            "latest_orders_data": latest_orders_data,
            "latest_payments_data": latest_payments_data,
            "labels": labels
        }

        return Response(response)



class AllOrdersView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrdersListSerializer
    queryset = Order.objects.all().order_by("date_created")

