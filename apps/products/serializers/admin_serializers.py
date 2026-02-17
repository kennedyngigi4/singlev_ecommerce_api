import json

from django.db import transaction
from rest_framework import serializers
from apps.products.models.models import *


class CategorySerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id","name", "thumbnail", "slug", "parent"
        ]
        read_only = [
            "id", "slug"
        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None


class CategoryChildrenSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            "id","name", "slug", "thumbnail", "parent", 
        ]
        


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "name", "image"
        ]
        read_only = [
            "id", "slug"
        ]


class FeatureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = [
            "id", "name", "priority"
        ]



class ProductVariantforProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "price",
            "discount_price",
            "size",
            "color",
            "stock",
            "sku",
            
        ]




class ProductWriteSerializer(serializers.ModelSerializer):
    variant = ProductVariantforProductCreateSerializer(write_only=True)

    class Meta:
        model = Product
        fields = [
            "name", "category", "brand", "description", "thumbnail", "variant", "features"
        ]


    def create(self, validated_data):
        variant_data = validated_data.pop("variant")
        features = validated_data.pop("features", [])

        with transaction.atomic():
            product = Product.objects.create(**validated_data)

            if features:
                product.features.set(features)

            ProductVariant.objects.create(
                product=product,
                **variant_data
            )    

        return product
    
    

class ProductVariantforProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id", "sku", "price", "discount_price", "is_active", "stock", "color", "size", "storage"
        ]

class ProductDetailsSerializer(serializers.ModelSerializer):
    variants = ProductVariantforProductSerializer(many=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    brand_id = serializers.CharField(source="brand.id", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    category_id = serializers.CharField(source="category.id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id","name", "category", "category_id", "brand", "brand_id", "description", "thumbnail", "features", "variants"
        ]

   



class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    

    class Meta:
        model = Product
        fields = [
            "id", "name", "category", "brand", "description", "thumbnail"
        ]

    


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "price",
            "discount_price",
            "size",
            "color",
            "sku",
            "product",
        ]
    

class ProductVariantListSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source="product.name", read_only=True)
    category = serializers.CharField(source="product.category.name", read_only=True)
    brand = serializers.CharField(source="product.brand.name", read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "price", "stock", "name", "category", "brand", "thumbnail"]


    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj:
            url = obj.thumbnail if obj.thumbnail else obj.product.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None