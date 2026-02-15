import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify

# Create your models here.


class UserManager(BaseUserManager):
    
    def create_user(self, email, fullname, phone, role, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            fullname=fullname,
            phone=phone,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, fullname, phone, role, password=None, **extra_fields):

        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)


        user = self.create_user(
            email=email,
            fullname=fullname,
            phone=phone,
            role=role,
            password=password,
            **extra_fields
        )
        return user



class User(AbstractBaseUser, PermissionsMixin):

    USER_ROLES = [
        ( "admin", "admin"),
        ( "manager", "manager"),
        ( "client", "client")
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(max_length=100)

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=70)
    phone = models.CharField(max_length=15)

    

    role = models.CharField(max_length=10, choices=USER_ROLES, default="client")

    date_joined = models.DateTimeField(auto_now_add=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'fullname', 'phone', 'role'
    ]

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.fullname)
            unique_suffix = uuid.uuid4().hex[:10]
            self.slug = f"{base_slug}-{unique_suffix}"

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.email)

