from django.contrib import admin

# Register your models here.

from .models import Account, Coupon, Message, Mail

admin.site.register(Account)
admin.site.register(Message)
admin.site.register(Coupon)
admin.site.register(Mail)
