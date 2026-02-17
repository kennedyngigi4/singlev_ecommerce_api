from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Max, Min

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response


from apps._helpers.product_helpers import get_category_ancestors, get_descendants
from apps.accounts.models.models import User
from apps.products.models.models import *
from apps.products.serializers.serializers import *

# Create your views here.
class FaeturesListView(generics.ListAPIView):
    serializer_class = FeaturesListSerializer
    queryset = Feature.objects.filter(is_active=True)


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.filter(
            parent__isnull=True
        )
        serializer = CategoryListSerializer(categories, many=True, context={"request": request})
        return Response(serializer.data)


class BrandListView(generics.ListAPIView):
    serializer_class = BrandListSerializer
    queryset = Brand.objects.order_by("name")
    



class HomepageFeatureListViewSet(ReadOnlyModelViewSet):
    serializer_class = FeatureProductsSerializer

    def get_queryset(self):
        return Feature.objects.filter(
                is_active=True
            ).order_by("priority").prefetch_related(
                Prefetch(
                "featured_list",
                queryset=Product.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        "variants",
                        queryset=ProductVariant.objects.filter(
                            is_active=True
                        ).only("id", "price", "thumbnail", "product"),
                        to_attr="default_variant"
                    )
                ).only("id", "name", "slug"),
                to_attr="homepage_products"
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

        
        if has_children:
            descendant_categories = get_descendants(category)

            products = Product.objects.filter(
                category__in=descendant_categories,
                is_active=True
            ).distinct().select_related("brand").prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(is_active=True).order_by("price"),
                    to_attr="default_variant"
                )
            )

            return Response({
                "type": "root" if is_root else "parent",
                "category": CategoryListSerializer(category).data,
                "breadcrumbs": breadcrumbs,
                "children": CategoryListSerializer(children, many=True).data,
                "products": ProductCardSerializer(
                    products,
                    many=True,
                    context={"request": request}
                ).data,
                "filters": self.get_filters(products)
            })

        # LEAF
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).distinct().select_related("brand").prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).order_by("price"),
                to_attr="default_variant"
            )
        )

        return Response({
            "type": "leaf",
            "category": CategoryListSerializer(category).data,
            "breadcrumbs": breadcrumbs,
            "children": [],
            "products": ProductCardSerializer(
                products,
                many=True,
                context={"request": request}
            ).data,
            "filters": self.get_filters(products)
        })
    
    def get_filters(self, products):
        return {
            "brands": products.values(
                "brand__id",
                "brand__name"
            ).distinct(),
            "price": {
                "min": products.aggregate(Min("variants__price"))["variants__price__min"],
                "max": products.aggregate(Max("variants__price"))["variants__price__max"],
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



