from django.db import transaction

from rest_framework import serializers
from apps.products.models.models import Product, ProductVariant, ProductImage
from apps.orders.models import Order, OrderItem



class ProductVariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "thumbnail",
            "price",
            "discount_price",
            "stock",
            "color",
            "size",
            "storage",
        ]



class ProductVariantCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "thumbnail", "price", "discount_price", "stock", "color", "size"
        ]


class ProductImageCreateSerializer(serializers.Serializer):
    image = serializers.ImageField()



class ProductCreateSerializer(serializers.ModelSerializer):

    variant = ProductVariantCreateSerializer(write_only=True)

    class Meta:
        model = Product
        fields = [
            "name", "category", "brand", "description", "thumbnail", "variant"
        ]


    def create(self, validated_data):
        variant_data = validated_data.pop("variant")
        features = variant_data.pop("features", [])

        with transaction.atomic():
            product = Product.objects.create(**validated_data)

            vari = ProductVariant.objects.create(
                product=product,
                **variant_data
            )    

            if features:
                vari.features.set(features)


        return product


class ProductCardSerializer(serializers.ModelSerializer):   
    variant_count = serializers.IntegerField(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "name", "category", "variant_count", "is_active"
        ]

