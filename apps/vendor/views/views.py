import json
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated

from apps.accounts.models.models import User
from apps.products.models.models import Product, ProductVariant, ProductImage, Category
from apps.vendor.services.vendor_services import VendorService

from apps.vendor.serializers.serializers import ProductCardSerializer, ProductCreateSerializer


# Create your views here.
class VendoDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        data = VendorService.get_dashboard_data(user)

        return Response(data)




class VendorProductsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = ProductCreateSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            
            serializer = serializer.save(created_by=self.request.user)
            
            return Response({ "success": True, "message": "Product created", "data": serializer.id}, status=status.HTTP_201_CREATED)
        
        
        return Response({ "success": False, "message": "Product creation failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        queryset = Product.objects.filter(
            created_by=self.request.user
        ).annotate(
            variant_count=Count("variants")
        ).order_by("-created_at")

        data = ProductCardSerializer(queryset, many=True).data
        return Response(data)

