from django.contrib import admin
from apps.products.models.models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Feature)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
