from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps._helpers.product_helpers import get_descendants
from apps.products.models.models import *
from apps.mobile.models.models import *
from apps.mobile.serializers.serializers import *
from apps.products.serializers.serializers import *
# Create your views here.


class MobileHomeView(APIView):

    def get(self, request):

        sliders = Slider.objects.filter(is_active=True).order_by("priority")
        top_categories = Category.objects.filter(parent__isnull=True)

        featured_items = Feature.objects.filter(
            is_active=True
        ).order_by("priority")

        response = {
            "featured_items": FeatureSerializer(
                featured_items,
                many=True,
                context={"request": request}
            ).data,
            "sliders": SlidersSerializer(sliders, many=True).data,
            "top_categories": CategorySerializer(
                top_categories,
                many=True,
                context={"request": request}
            ).data
        }

        return Response(response)


class MobileCategoriesView(generics.ListAPIView):
    serializer_class = MobileCategoriesSerializer
    queryset = Category.objects.filter(parent__isnull=True, is_active=True)




class MobileCategoryTreeView(APIView):

    def get(self, request, root_id):
        root = get_object_or_404(
            Category,
            id=root_id,
            parent=None
        )

        serializer = CategoryTreeSerializer(
            root,
            context={"request": request}
        )

        

        return Response(serializer.data)





def get_all_descendants(category):
    descendants = []

    children = Category.objects.filter(parent=category, is_active=True)

    for child in children:
        descendants.append(child)
        descendants.extend(get_all_descendants(child))

    return descendants



class MobileCategoryProductsView(APIView):

    def get(self, request, category_id):
        category = get_object_or_404(
            Category,
            id=category_id,
            is_active=True
        )

        # Get all children recursively
        descendants = get_all_descendants(category)

        # Include the clicked category itself
        categories = [category] + descendants

        variants = ProductVariant.objects.filter(
            product__category__in=categories,
            product__is_active=True
        ).select_related("product")

        serializer = CategoryProductsSerializer(
            variants,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


