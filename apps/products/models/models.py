import uuid
from django.db import models
from django.utils.text import slugify


from apps.accounts.models.models import User
from apps.products.upload_paths import (product_images_path, product_thumbnail_path, product_variant_thumbnail_path)

# Create your models here.


class Feature(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=70, unique=True)

    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=1)

    title_color = models.CharField(max_length=20, blank=True, default="#FFFFFF")
    bg_title_color = models.CharField(max_length=20, blank=True, default="#008000")



    def __str__(self):
        return str(self.name)



class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)

    name = models.CharField(max_length=70, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="products/categories/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug

        super().save( *args, **kwargs)


    def __str__(self):
        return str(self.name)
    

class Brand(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)
    
    name = models.CharField(max_length=70, unique=True)
    image = models.ImageField(upload_to="products/brands")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug

        super().save( *args, **kwargs)
        

    def __str__(self):
        return str(self.name)





class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=1000, unique=True)

    name = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    thumbnail = models.ImageField(upload_to=product_thumbnail_path)
    description = models.TextField(blank=True)

    features = models.ManyToManyField(Feature, related_name="featured_list", blank=True)
    tags = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="products_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="products_updated")


    @property
    def default_variant(self):
        return self.variants.filter(is_active=True).order_by("created_at").first()

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name
            
            if self.brand:
                base = slugify(f"{self.name}-{self.brand.name}")
                unique_suffix = uuid.uuid4().hex[:10]

            self.slug = f"{base}-{unique_suffix}"

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return str(self.name)
    





class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )


    thumbnail = models.ImageField(upload_to=product_variant_thumbnail_path, null=True, blank=True)

    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    stock = models.PositiveIntegerField(default=1, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    color = models.CharField(max_length=30, blank=True)
    size = models.CharField(max_length=20, blank=True)
    storage = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "product",
            "color",
            "size",
            "storage",
        )
        
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]


    @property
    def display_thumbnail(self):
        return self.thumbnail or self.product.thumbnail



    def __str__(self):
        attrs = " / ".join(
            filter(None, [self.color, self.size, self.storage])
        )
        return f"{self.product.name} ({attrs})"



    




class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_path)

    def __str__(self):
        return str(self.product.name)

