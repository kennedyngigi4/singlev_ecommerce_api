from rest_framework import serializers
from apps.orders.models import *



class AdminOrdersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "order_id", "total_amount", "quantity", "payment_status", "status"
        ]


