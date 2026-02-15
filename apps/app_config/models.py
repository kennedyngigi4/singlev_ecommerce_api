
import uuid
from django.db import models

# Create your models here.


class MpesaConfig(models.Model):

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=255)
    passkey = models.CharField(max_length=255)
    
    environment = models.CharField(max_length=55)

    callback_url = models.URLField()

    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.shortcode} - {self.is_active}"


