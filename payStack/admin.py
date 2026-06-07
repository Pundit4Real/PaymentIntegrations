from django.contrib import admin
from payStack.models import Payment

# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['amount','email','ref','verified', 'date_created']

admin.site.register(Payment,PaymentAdmin)