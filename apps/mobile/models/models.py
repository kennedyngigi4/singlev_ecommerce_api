import uuid
from django.db import models
from django.db.models import Max

# Create your models here.


class Slider(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    image = models.ImageField(upload_to="images/mobile/sliders")
    priority = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.priority is None:
            max_priority = Slider.objects.aggregate(
                Max("priority")
            )["priority__max"]

            self.priority = (max_priority or 0) + 1

        super().save(*args, **kwargs)


