from rest_framework import serializers
from apps.products.models.models import *


class FeaturesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = [
            "id", "name", "priority"
        ]

class CategoryListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "thumbnail", "children"
        ]

    def get_children(self, obj):
        qs = obj.children
        return CategoryListSerializer(qs, many=True).data

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None


class CategoryBreadcrumbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]




class BrandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id", "name", "slug", "image",
        ]


class ProductCardSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    thumbnail = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.ListField()

    def to_representation(self, product):
        request = self.context.get("request")

        variant = getattr(product, "default_variant", None)

        image = (
            variant.thumbnail
            if variant and variant.thumbnail
            else product.thumbnail
        )

        image_url = (
            request.build_absolute_uri(image.url)
            if image and request
            else image.url if image else None
        )

        return {
            "id": variant.id,
            "name": product.name,
            "slug": product.slug,
            "thumbnail": image_url,
            "price": variant.price if variant else None,
            "category": product.category.slug,
        }



class FeatureProductsSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = [
            "id", "name", "priority", "bg_title_color", "title_color", "products"
        ]

    def get_products(self, obj):
        request = self.context.get("request") 
        return ProductCardSerializer(
            obj.homepage_products[:12],
            many=True,
            context={'request': request}
        ).data



class ProductVariantSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "price",
            "discount_price",
            "thumbnail",
            "color",
            "size",
            "storage",

        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url

        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.CharField(source="category.name", read_only=True)
    brand = serializers.CharField(source="brand.name", read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    default_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "brand",
            "thumbnail",
            "variants",
            "default_variant"
        ]


    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_default_variant(self, obj):
        variant = obj.variants.filter(is_active=True).first()
        if not variant:
            return None

        return {
            "id": variant.id,
            "price": variant.price,
            "discount_price": variant.discount_price,
        }
    
    


