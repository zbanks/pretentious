# Create your views here.
from models import *
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    balance = forms.DecimalField(max_digits=5, decimal_places=2, required=False)

    

def index(request):
    products = Product.objects.filter(is_active=True)
    return render_to_response('index.html', {"products": products})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render_to_response("signup.html", {"form": form})
