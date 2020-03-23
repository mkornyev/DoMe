# Imports 

from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

# Create your views here.

def home(request): 
    context = {}
    return render(request, 'doMe/base.html', context)

def login(request):
    context = {}
    return render(request, 'doMe/base.html', context)

@login_required
def logout(request):
    context = {}
    return render(request, 'doMe/base.html', context)

def about(request):
    context = {}
    return render(request, 'doMe/base.html', context)