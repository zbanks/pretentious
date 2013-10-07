from django.db import models
from django.db.models import Sum, Avg
from django.contrib.auth.models import User
from django.db.models.signals import * 

import hashlib
import logging
logger = logging.getLogger(__name__)

# Create your models here.

def gravatar(cust):
    return "http://www.gravatar.com/avatar/%s?d=identicon" % hashlib.md5(cust.user.email).hexdigest()

class Customer(models.Model):
    user = models.OneToOneField(User)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    require_password = models.BooleanField(default=False)
    is_trusted = models.BooleanField(default=False)
    avatar = models.URLField(blank=True)
    def recalculate(self, **kwargs):
        self.balance = self.transaction_set.all().aggregate(Sum('credit'))["credit__sum"]
        self.save()
    def __str__(self):
        return self.user.username
    class Meta:
        ordering = ["user__username"]

class Product(models.Model):
    name = models.CharField(max_length=80)
#generic = models.CharField(max_length=80)
    slug = models.SlugField()
    image = models.URLField(blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    ordering = models.SmallIntegerField()
    shortcut = models.CharField(max_length=4)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["ordering", "is_active"]

class Barcode(models.Model):
    product = models.ForeignKey(Product, null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    text = models.CharField(max_length=120, blank=True)
    sha1text = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)
    class Meta:
        pass

class InputLog(models.Model):
    text = models.TextField()
    customer = models.ForeignKey(Customer, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    barcode_match = models.BooleanField(default=False)
    special_match = models.BooleanField(default=False)

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, null=True, blank=True)
    product = models.ForeignKey(Product, null=True, blank=True)
    credit = models.DecimalField(max_digits=4, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    void = models.BooleanField(default=False)
    def __str__(self):
        return "%s - %s ($%0.2f)" % (self.customer, self.product, self.credit)
    class Meta:
        pass

class Stocking(models.Model):
    user = models.ForeignKey(Customer, null=True, blank=True)
    product = models.ForeignKey(Product)
    quantity = models.SmallIntegerField()
    cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    in_machine = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%d)" % (self.product, self.quantity)
    class Meta:
        pass

def recalculate_balance(sender, instance, **kwargs):
    if instance.customer:
        instance.customer.recalculate()

def update_sha1text(sender, instance, **kwargs):
    if instance.text:
        instance.sha1text = hashlib.sha1(instance.text).hexdigest()

post_save.connect(recalculate_balance, sender=Transaction)
pre_delete.connect(recalculate_balance, sender=Transaction)
pre_save.connect(update_sha1text, sender=Barcode)

