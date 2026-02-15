from rest_framework import serializers
from apps.orders.models import Order, OrderItem


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "product", "quantity", "price"
        ]


class OrderWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "total_amount", "quantity", "mpesa_number"
        ]


class OrderItemReadSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.product.name", read_only=True)
    product_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_thumbnail", "quantity", "price", "status"
        ]

    def get_product_thumbnail(self, obj):
        request = self.context.get("request")
        if (
            obj.product
            and obj.product.product
            and obj.product.product.thumbnail
        ):
            thumbnail = obj.product.product.thumbnail
            return request.build_absolute_uri(thumbnail.url) if request else thumbnail.url

        return None
    

class OrderReadSerializer(serializers.ModelSerializer):
    order_items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
           "id", "order_id", "total_amount", "quantity", "mpesa_number", "date_created", "status", "payment_status", "order_items"
        ]    



class OrderForItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
           "id", "order_id", "total_amount", "quantity", "mpesa_number", "date_created", "status", "payment_status"
        ]   

class OrderItemWithOrderSerializer(serializers.ModelSerializer):
    order = OrderForItemSerializer(read_only=True)
    product = serializers.CharField(source="product.product.name", read_only=True)
    product_thumbnail = serializers.SerializerMethodField()

   

    class Meta:
        model = OrderItem
        fields = [
            "order", "product", "product_thumbnail", "quantity", "price", "status"
        ]

    def get_product_thumbnail(self, obj):
        request = self.context.get("request")
        if (
            obj.product
            and obj.product.product
            and obj.product.product.thumbnail
        ):
            thumbnail = obj.product.product.thumbnail
            return request.build_absolute_uri(thumbnail.url) if request else thumbnail.url

        return None
    



class STKPushSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    amount = serializers.CharField()



