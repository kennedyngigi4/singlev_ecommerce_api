from django.contrib import admin

from apps.accounts.models.models import User
from apps.accounts.models.customer_profile import *
# Register your models here.


admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(CustomerLocation)



