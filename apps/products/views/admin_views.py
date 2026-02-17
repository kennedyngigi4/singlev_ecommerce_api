from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.products.models.models import *
from apps.products.serializers.admin_serializers import *


class FeatureViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Feature.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == "create":
            return FeatureListSerializer
        elif self.action == "list":
            return FeatureListSerializer
        else:
            return FeatureListSerializer
        

    def create(self, request):
        pass

    
    def list(self, request):
        serializer = self.get_serializer(self.queryset(), many=True)
        return Response(serializer.data)
    


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("name")

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True, "message": "Category created."}, status=status.HTTP_201_CREATED)

        return Response({ "success": False, "message": "An error occured.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        categories = Category.objects.all().order_by("name")
        serializer = CategorySerializer(
            categories,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(category)
        return Response({ "success": True, "data": serializer.data })


    def partial_update(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True, "message": "Category updated successfully.", "data": serializer.data})


        return Response({ "success": False, "message": "Update failed.", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        category.delete()
        return Response({ "success": True, "message": "Category deleted successfully." }, status=status.HTTP_204_NO_CONTENT)



class CategoryChildrenView(generics.ListAPIView):
    serializer_class = CategoryChildrenSerializer
    queryset = Category.objects.filter(children__isnull=True)


class BrandViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = BrandSerializer
    queryset = Brand.objects.all().prefetch_related("category").order_by("name")


    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True, "message": "Brand created."}, status=status.HTTP_201_CREATED)
        return Response({ "success": False, "message": "Brand creation failed.", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        brand = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(brand)
        return Response({ "success": True, "data": serializer.data})


    def partial_update(self, request, pk=None):
        brand = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(brand, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True, "message": "Brand updated successfully.", "data": serializer.data})

        return Response({ "success": False, "message": "Update failed.", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        brand = get_object_or_404(self.get_queryset(), pk=pk)

        brand.delete()

        return Response({ "success": True, "message": "Brand deleted." }, status=status.HTTP_204_NO_CONTENT)




class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()


    def get_serializer_class(self):
        if self.action == "create":
            return ProductWriteSerializer
        elif self.action in ["update", "partial_update"]:
            return ProductWriteSerializer
        elif self.action == 'list':
            return ProductVariantListSerializer
        elif self.action == "retrieve":
            return ProductDetailsSerializer
        else:
            return ProductDetailsSerializer
        
    
    def get_queryset(self):
        if self.action == "retrieve":
            return Product.objects.select_related("brand", "category").prefetch_related("variants")
        elif self.action == "list":
            return ProductVariant.objects.select_related("product", "product__brand", "product__category")
        return Product.objects.all()

        

    def create(self, request):
        
        serializer = self.get_serializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            
            serializer = serializer.save(created_by=self.request.user)
            
            return Response({ "success": True, "message": "Product created", "data": serializer.id}, status=status.HTTP_201_CREATED)
        
        
        return Response({ "success": False, "message": "Product creation failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({
                "success": True,
                "message": "Product updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "message": "Product update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    


class ProductVariantCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductVariantCreateSerializer
    queryset = ProductVariant.objects.all()

    def create(self, request):
        serializer = ProductVariantCreateSerializer(data=request.data)
        print(request.data)

        if serializer.is_valid():
            variant = serializer.save()
            print(variant)
            return Response({ "success": True, "message": "Product added."}, status=status.HTTP_200_OK)
        
        print(serializer.error_messages)
        return Response({ "success": False, "message": "An error occured", "errors": serializer.errors}, status=status.HTTP_200_OK)

