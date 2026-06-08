from django.db import transaction

from rest_framework import serializers

from apps.accounts.models.models import User
from apps.accounts.models.vendor_profile import VendorProfile
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


class VendorCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField()
    phone = serializers.CharField()
    role = serializers.CharField()
    password = serializers.CharField(write_only=True)

    business_name = serializers.CharField()
    business_phone = serializers.CharField()
    business_location = serializers.CharField()
    business_status = serializers.CharField()


    @transaction.atomic
    def create(self, validated_data):
        manager = self.context["request"].user

        user = User.objects.create_user(
            fullname=validated_data["fullname"],
            email=validated_data["email"],
            role=validated_data["role"],
            phone=validated_data["phone"],
            password=validated_data["password"],
        )


        vendor = VendorProfile.objects.create(
            user=user,
            business_name=validated_data["business_name"],
            business_phone=validated_data["business_phone"],
            business_location=validated_data["business_location"],
            business_status=validated_data["business_status"],
            created_by=manager
        )


        return vendor
    

    def validate_business_name(self, value):
        if VendorProfile.objects.filter(business_name__iexact=value).exists():
            raise serializers.ValidationError(
                "A vendor with this business name already exists."
            )
        return value




class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [
            "id",
            "business_name",
            "business_phone",
            "business_location",
            "business_status",
        ]

class ManagerVendorsSerializer(serializers.ModelSerializer):
    vendors = VendorProfileSerializer(source="vendor_creator", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "fullname", "email", "vendors"]



