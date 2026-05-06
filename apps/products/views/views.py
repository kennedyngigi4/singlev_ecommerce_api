from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Max, Min
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response

from apps._helpers.product_helpers import get_category_ancestors, get_descendants
from apps.accounts.models.models import User
from apps.products.models.models import *
from apps.products.serializers.serializers import *



#==========================================================================================
# VIEWS HERE
#==========================================================================================


@method_decorator(cache_page(60 * 60 * 24), name="dispatch")
class FaeturesListView(generics.ListAPIView):
    serializer_class = FeaturesListSerializer
    queryset = Feature.objects.filter(is_active=True)


@method_decorator(cache_page(60 * 60 * 24 * 14), name="dispatch")
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.filter(
            parent__isnull=True
        )
        serializer = CategoryListSerializer(categories, many=True, context={"request": request})
        return Response(serializer.data)


@method_decorator(cache_page(60 * 60 * 10), name="dispatch")
class BrandListView(generics.ListAPIView):
    serializer_class = BrandListSerializer
    queryset = Brand.objects.order_by("name")
    


@method_decorator(cache_page(60 * 60 * 10), name="dispatch")
class HomepageFeatureListViewSet(ReadOnlyModelViewSet):
    serializer_class = FeatureProductsSerializer

    def get_queryset(self):
        return Feature.objects.filter(is_active=True).order_by("priority").prefetch_related(
            Prefetch(
                "variants",  
                queryset=ProductVariant.objects.filter(is_active=True)
                .select_related("product", "product__category")
                .only(
                    "id", "price", "thumbnail",
                    "product__id", "product__name", "product__slug",
                    "product__thumbnail",
                    "product__category__slug"
                ),
                to_attr="homepage_variants"
            )
        )



class CategoryProductsView(APIView):

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)

        breadcrumbs = CategoryBreadcrumbSerializer(
            get_category_ancestors(category),
            many=True
        ).data

        children = category.children.filter(is_active=True)
        is_root = category.parent is None
        has_children = children.exists()

        # If category has children, include descendants
        if has_children:
            descendant_categories = get_descendants(category)

            variants = ProductVariant.objects.select_related(
                "product",
                "product__brand",
                "product__category"
            ).filter(
                product__category__in=descendant_categories,
                product__is_active=True,
                is_active=True
            ).order_by("price")

            return Response({
                "type": "root" if is_root else "parent",
                "category": CategoryListSerializer(category, context={"request": request}).data,
                "breadcrumbs": breadcrumbs,
                "children": CategoryListSerializer(children, many=True, context={"request": request}).data,
                "products": ProductCardSerializer(
                    variants,
                    many=True,
                    context={"request": request}
                ).data,
                "filters": self.get_filters(variants)
            })

        # LEAF category (no children)
        variants = ProductVariant.objects.select_related(
            "product",
            "product__brand",
            "product__category"
        ).filter(
            product__category=category,
            product__is_active=True,
            is_active=True
        ).order_by("price")

        return Response({
            "type": "leaf",
            "category": CategoryListSerializer(category, context={"request": request}).data,
            "breadcrumbs": breadcrumbs,
            "children": [],
            "products": ProductCardSerializer(
                variants,
                many=True,
                context={"request": request}
            ).data,
            "filters": self.get_filters(variants)
        })

    def get_filters(self, variants):
        return {
            "brands": variants.values(
                "product__brand__id",
                "product__brand__name"
            ).distinct(),

            "price": {
                "min": variants.aggregate(Min("price"))["price__min"],
                "max": variants.aggregate(Max("price"))["price__max"],
            }
        }



class ProductByCategorySlugView(APIView):

    def get(self, request, category_slug, product_slug):
        product = get_object_or_404(
            Product.objects
            .select_related("brand", "category")
            .prefetch_related(
                "category",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(is_active=True)
                )
            ),
            slug=product_slug,
            category__slug=category_slug,
            is_active=True,
        )

        serializer = ProductDetailSerializer(product, context={"request": request})

        
        return Response(serializer.data)




class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            "brand"
        ).prefetch_related(
            "variants",
            "variants__images",
            "category",
        )



