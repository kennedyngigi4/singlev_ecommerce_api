from rest_framework import serializers

from apps.orders.models import *
from apps.payments.models import *

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
           "id", "order_id", "quantity", "total_amount", "status", "payment_status"
        ]   

class OrderItemSerializer(serializers.ModelSerializer):
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
    

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = [
            "id", "transaction_code", "phone_number", "amount", "status", "created_at"
        ]
    

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
           "id", "order_id", "quantity", "total_amount", "mpesa_number", "date_created", 
           "status", "payment_status", "order_items", "payments"
        ]   


class ProductForVariantSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id","name", "category", "brand", "is_active"
        ]


class ProductVariantWithProductListSerializer(serializers.ModelSerializer):
    product = ProductForVariantSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id","price", "product", "thumbnail"
        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")
        
        image = (
            obj.thumbnail 
            if obj.thumbnail 
            else obj.product.thumbnail
        )

        image_url = (
            request.build_absolute_uri(image.url)
            if image
            else image.url if image else None
        )

        return image_url

