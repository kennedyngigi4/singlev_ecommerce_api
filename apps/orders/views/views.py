from decimal import Decimal
from django.shortcuts import render
from django.db import transaction

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps._helpers.payments.mpesa import MpesaService
from apps.orders.serializers.serializers import *
from apps.orders.services.services import OrderService
from apps.products.models.models import *
# Create your views here.


class OrdersView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = self.request.user

        cart = request.data.get("products", [])
        mpesa_phone = request.data.get("mpesa_number")

        if not cart:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total = Decimal(0.0)
        quantity = 0

        order = Order.objects.create(
            user=user,
            total_amount=total,
            quantity=0,
            payment_status="pending",
            status="pending",
            mpesa_number=mpesa_phone
        )

        for item in cart:
            product = ProductVariant.objects.select_for_update().get(id=item["id"])

            line_total = product.price * item["quantity"]
            line_quantity = item["quantity"]

            total += line_total
            quantity += line_quantity

            OrderItem.objects.create(
                product=product,
                order=order,
                price=product.price,
                quantity=item["quantity"],
                status="pending"
            )

        order.total_amount = total
        order.quantity = quantity
        order.save()

        OrderService().mpesa_order(order)


        return Response({ "success": True, "message": "Order successful."}, status=status.HTTP_201_CREATED)



class MyOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemWithOrderSerializer
    

    def get_queryset(self):
        user = self.request.user

        return (
            OrderItem.objects
            .select_related("order", "product", "product__product")
            .filter(order__user=user)
            .order_by("-order__date_created")
        )
    

class OrderDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderReadSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Order.objects.prefetch_related("order_items").filter(user=self.request.user)
    



class OrderPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        mpesa_number = request.data.get("mpesa_number")
        total_amount = request.data.get("total_amount")

        order = Order.objects.get(order_id=order_id)

        if not order:
            return Response({ "success": False, "message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if order.total_amount:
            mpesa = MpesaService()
            response = mpesa.stk_push(phone_number=mpesa_number, amount=int(order.total_amount), reference=f"ORDER {order_id}")
            order.checkout_request_id = response["CheckoutRequestID"]
            order.merchant_request_id = response["MerchantRequestID"]
            order.save(update_fields=["checkout_request_id", "merchant_request_id"])

            return Response({ "success": True, "message": "Check your phone and enter mpesa pin."}, status=status.HTTP_200_OK)



