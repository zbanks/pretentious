from django.contrib.admin import *
from models import *

class CustomerAdmin(ModelAdmin):
    list_display = ('user', 'balance', 'require_password', 'is_trusted')
    list_filter = ('require_password', 'is_trusted')
    list_editable = ('is_trusted',)

class ProductAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'price', 'ordering', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('price', 'ordering', 'is_active')

class TransactionAdmin(ModelAdmin):
    list_display = ('customer', 'product', 'credit', 'time')

class StockingAdmin(ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'cost', 'time')

site.register(Customer, CustomerAdmin)
site.register(Product, ProductAdmin)
site.register(Transaction, TransactionAdmin)
site.register(Stocking, StockingAdmin)
