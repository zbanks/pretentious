# Create your views here.
from models import *
from django.shortcuts import render_to_response

def index(request):
    products = Product.objects.filter(is_active=True)
    return render_to_response('index.html', {"products": products})
