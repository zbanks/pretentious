from django.contrib.admin import *
from models import *

class CustomerAdmin(ModelAdmin):
    list_display = ('user', 'balance', 'require_password', 'is_trusted')
    list_filter = ('require_password', 'is_trusted')
    list_editable = ('is_trusted',)

class ProductAdmin(ModelAdmin):
    list_display = ('slug', 'name', 'price', 'ordering', 'shortcut', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('name', 'price', 'ordering', 'is_active', 'shortcut')

class TransactionAdmin(ModelAdmin):
    list_display = ('customer', 'product', 'credit', 'time', 'void')
    list_editable = ('void',)

class StockingAdmin(ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'cost', 'in_machine', 'time')

class BarcodeAdmin(ModelAdmin):
    list_display = ('product', 'customer', 'text', 'is_active')
    list_editable = ('text', 'is_active')
    list_filter = ('is_active',)


site.register(Customer, CustomerAdmin)
site.register(Product, ProductAdmin)
site.register(Transaction, TransactionAdmin)
site.register(Stocking, StockingAdmin)
site.register(Barcode, BarcodeAdmin)
