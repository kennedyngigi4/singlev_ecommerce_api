from rest_framework import serializers
from apps.products.models.models import *
from apps.mobile.models.models import *



class SlidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = [
            "id", "image", "priority", "is_active"
        ]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "children"]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).prefetch_related("children")

        return CategoryTreeSerializer(
            children,
            many=True,
            context=self.context
        ).data


class MobileCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id", "name", "thumbnail",
        ]


class ProductCardSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "thumbnail", "price"
        ]


    def get_thumbnail(self, obj):
        request = self.context.get("request")
        variant = getattr(obj, "default_variant", None)  

        if variant and variant.thumbnail:
            return request.build_absolute_uri(variant.thumbnail.url)
        

        if obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)

        return None

    def get_price(self, obj):
        variant = getattr(obj, "default_variant", None)
        if variant:
            return int(variant.price)
        return None


class FeatureVariantSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "price",
            "thumbnail",
            "name",
            "thumbnail",
        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)

        if obj.product.thumbnail:
            return request.build_absolute_uri(obj.product.thumbnail.url)

        return None


class FeatureSerializer(serializers.ModelSerializer):

    variants = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = [
            "id",
            "name",
            "is_active",
            "priority",
            "bg_title_color",
            "title_color",
            "variants",
        ]

    def get_variants(self, obj):
        request = self.context.get("request")

        products = obj.featured_list.all()

        variants = ProductVariant.objects.filter(
            product__in=products,
            is_active=True
        ).select_related("product")

        return FeatureVariantSerializer(
            variants,
            many=True,
            context={"request": request}
        ).data




class CategoryProductsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "price",
            "thumbnail",
            "name",
        ]

    def get_thumbnail(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)

        if obj.product.thumbnail:
            return request.build_absolute_uri(obj.product.thumbnail.url)

        return None


