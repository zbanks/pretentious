# Create your views here.
from models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

import subprocess
import re

class SignupForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=20)
    name = forms.CharField(max_length=30)
    balance = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).count() is not 0:
            raise forms.ValidationError("Username %s already taken" % username)
        return username
    

def index(request):
    products = Product.objects.filter(is_active=True).order_by("ordering")
    display_products = [None]*9
    for product in products:
        if 1 <= product.ordering <= 9:
            display_products[product.ordering-1] = product
    customers = Customer.objects.all()
    return render_to_response('index.html', RequestContext(request, {"products": products,
                                                                     "display_products": display_products,
                                                                     "customers": customers,
                                                                     "range10": range(10)}))

def buy(request):
    if "username" in request.REQUEST and "product" in request.REQUEST:
        username = request.REQUEST["username"]
        product_slug = request.REQUEST["product"]
        customer = Customer.objects.filter(user__username=username)
        product = Product.objects.filter(slug=product_slug)
        if customer.exists() and product.exists():
            customer = customer.get()
            product = product.get()
            t = Transaction(customer=customer, product=product, credit=-product.price)
            t.save()
            messages.success(request, "Bought %s as %s for %0.2f." % (product.name, username, product.price))
            return HttpResponseRedirect("/")
    messages.error(request, "Invalid purchase")
    return HttpResponseRedirect("/") 

def credit(request):
    if "username" in request.REQUEST and "credit" in request.REQUEST:
        username = request.REQUEST["username"]
        credit = float(request.REQUEST["credit"])    
        customer = Customer.objects.filter(user__username=username)
        if customer.exists():
            customer = customer.get()
            t = Transaction(customer=customer, credit=credit)
            t.save()
            messages.success(request, "Added $%0.2f credit to %s." % (credit, username))
            return HttpResponseRedirect("/")
    messages.error(request, "Invalid credit")
    return HttpResponseRedirect("/")

def transfer(request):
    if "username" in request.REQUEST and "recipient" in request.REQUEST and "amount" in request.REQUEST:
        username = request.REQUEST["username"]
        recipient = request.REQUEST["recipient"]
        amount = float(request.REQUEST["amount"])
        try:
            from_cust = Customer.objects.get(user__username=username)
            to_cust = Customer.objects.get(user__username=recipient)
        except:
            messages.error(request, "Invalid customer/recipient")
            return HttpResponseRedirect("/")
        t = Transaction(customer=from_cust, credit=-amount)
        t.save()
        t2 = Transaction(customer=to_cust, credit=amount)
        t2.save()
        messages.success(request, "Transfered $%0.2f from %s to %s" % (amount, username, recipient))
    return HttpResponseRedirect("/")


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            cu = User()
            cu.first_name = form.cleaned_data["name"]
            cu.username = form.cleaned_data["username"]
            cu.email = form.cleaned_data["email"]
            cu.set_password('password')
            cu.save()
            c = Customer(user=cu)
            c.save()
            t = Transaction(customer=c, credit=form.cleaned_data["balance"])
            t.save()
            messages.add_message(request, messages.INFO, "Created user %s" % c.user.username)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render_to_response("signup.html", RequestContext(request, {"form": form}))

def finger(request, kerberos):
    directory = subprocess.check_output(["finger", "%s@mit" % kerberos]) 
    for line in directory.split("\n"):
        m = re.match(r"^ +name[:] (\w+)\, (\w+) .*", line)
        if m and len(m.groups()) == 2:
            groups = m.groups()
            return HttpResponse("%s %s" % (groups[1], groups[0]))
    return HttpResponse("")
