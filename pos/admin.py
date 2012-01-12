from django.contrib.admin import *
from models import *

class CustomerAdmin(ModelAdmin):
    pass

class ProductAdmin(ModelAdmin):
    pass

class TransactionAdmin(ModelAdmin):
    pass

class StockingAdmin(ModelAdmin):
    pass

site.register(Customer, CustomerAdmin)
site.register(Product, ProductAdmin)
site.register(Transaction, TransactionAdmin)
site.register(Stocking, StockingAdmin)
