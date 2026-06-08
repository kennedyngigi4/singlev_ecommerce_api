from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
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


class VendorViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = VendorCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Vendor created successfully."
            }, status=status.HTTP_201_CREATED)
        

        first_error = next(iter(serializer.errors.values()))[0]
        return Response({
                "success": False,
                "errors": str(first_error[0]) if isinstance(first_error, list) else str(first_error)
        }, status=status.HTTP_400_BAD_REQUEST)

    
    def list(self, request):
        manager = self.request.user

        vendors = VendorProfile.objects.filter(created_by=manager)
        serializer = VendorProfileSerializer(vendors, many=True)
        return Response({
            "success": True,
            "vendors": serializer.data
        }, status=status.HTTP_200_OK)


    def retrieve(self, request, pk=None):
        manager = self.request.user

        vendor = get_object_or_404(VendorProfile, id=pk, created_by=manager)
        serializer = VendorProfileSerializer(vendor)
        return Response({ "success": True, "vendor": serializer.data }, status=status.HTTP_200_OK)


    def partial_update(self, request, pk=None):
        manager = self.request.user
        vendor = get_object_or_404(VendorProfile, id=pk, created_by=manager)
        serializer = VendorCreateSerializer(vendor, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Vendor updated successfully.",
            }, status=status.HTTP_202_ACCEPTED)
        
        first_error = next(iter(serializer.errors.values()))

        if isinstance(first_error, list):
            first_error = first_error[0]
        return Response({ "success": False, "errors": str(first_error)}, status=status.HTTP_400_BAD_REQUEST )


    def destroy(self, request, pk=None):
        manager = self.request.user

        vendor = get_object_or_404(VendorProfile, id=pk, created_by=manager)
        vendor.delete()

        return Response({
            "success": True,
            "message": "Vendor deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)

