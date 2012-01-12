from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    require_password = models.BooleanField(default=False)
    is_trusted = models.BooleanField(default=False)
    avatar = models.URLField(blank=True)
    def __str__(self):
        return self.user.username
    class Meta:
        pass

class Product(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()
    image = models.URLField(blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    ordering = models.SmallIntegerField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["ordering", "is_active"]

class Transaction(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product, null=True, blank=True)
    credit = models.DecimalField(max_digits=4, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s - %s ($%0.2f)" % (self.customer, self.product, self.credit)
    class Meta:
        pass

class Stocking(models.Model):
    user = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    quantity = models.SmallIntegerField()
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s (%d)" % (self.product, self.quantity)
    class Meta:
        pass
    
