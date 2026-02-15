from django.shortcuts import render

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import *
from apps.products.models.models import *
from apps.manager.serializers import *


# Create your views here.


class StatsDashboardView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = self.request.user

        if user.role != "manager":
            return Response({ "success": False, "message": "You are not allowed in this area."}, status=status.HTTP_403_FORBIDDEN)
        
        total_products = ProductVariant.objects.count()
        out_of_stock_products = ProductVariant.objects.filter(is_active=False).count()
        pending_orders_count = Order.objects.filter(payment_status="paid", status="pending").count()
        in_transit_orders = Order.objects.filter(status="in_transit").count()
        
        latest_orders = OrderListSerializer(Order.objects.all().order_by("-date_created")[:10], many=True)

        response = {
            "total_products": total_products,
            "out_of_stock_products": out_of_stock_products,
            "pending_orders_count": pending_orders_count,
            "in_transit_orders": in_transit_orders,
            "latest_orders": latest_orders.data,
        }

        return Response(response)


class AllProductsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = self.request.user

        if user.role != "manager":
            return Response({ "success": False, "message": "You are not allowed in this area."}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = (
            ProductVariant.objects
            .select_related("product")
            .order_by("product__created_at")
        )

        serializer = ProductVariantWithProductListSerializer(queryset, many=True, context={ "request": request })
        return Response(serializer.data)
    


class AllOrdersView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request):
        user = self.request.user

        if user.role != "manager":
            return Response({ "success": False, "message": "You are not allowed in this area."}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = (
            Order.objects
            .order_by("-date_created")
        )

        serializer = OrderListSerializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)



class OrderDetailsView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request, pk):
        user = self.request.user

        if user.role != "manager":
            return Response({ "success": False, "message": "You are not allowed in this area."}, status=status.HTTP_403_FORBIDDEN)
        

        queryset = (
            Order.objects
            .prefetch_related(
                "order_items__product__product", "payments"
            )
            .get(id=pk)
        )

        serializer = OrderSerializer(queryset, context={"request": request})
        return Response(serializer.data)



class DispatchOrderView(APIView):
    permission_classes = [ IsAuthenticated ]

    def patch(self, request):
        user = self.request.user

        if user.role != "manager":
            return Response({ "success": False, "message": "You are not allowed in this area."}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = request.data.get("id")
        new_status = request.data.get("status")

        print(id)

        if not order_id:
            return Response(
                {"success": False, "message": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.get(id=order_id)

        if not order:
            return Response({
                "success": False,
                "message": "Order not found."
            }, status=status.HTTP_404_NOT_FOUND)
        

        if order.payment_status != "paid":
            return Response({
                "success": False,
                "message": "Order has not been paid."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save(update_fields=["status"])

        return Response({
            "success": True,
            "message": "Order dispatched successfully.",
            "data": {
                "order_id": order.id,
                "status": order.status
            }
        })

