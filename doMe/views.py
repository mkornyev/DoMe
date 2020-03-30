# Imports 

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from doMe.forms import LoginForm, RegistrationForm
from doMe.models import Workspace, Profile, toDoItem


# Create your views here.

def landingPage(request): 
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	context = {} 
	context['loginForm'] = LoginForm()
	context['registrationForm'] = RegistrationForm()
	return render(request, 'doMe/landing.html', context)

def register(request):
	if request.method != 'POST':
		return 

	context = {}
	context['registrationForm'] = RegistrationForm(request.POST)

	if not form.is_valid():
		context['loginForm'] = LoginForm()
		return render(request, 'doMe/landing.html', context)

	user = User.objects.create_user(username=form.cleaned_data['username'], 
										password=form.cleaned_data['password'],
										email=form.cleaned_data['email'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
	user.save()

	profile = Profile(user=user)
	profile.save() 

	workspace = Workspace(title='My Workspace', description='Your personal workspace. See your global ToDos here.')
	workspace.save()
	workspace.members.add(profile)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)

	return redirect(reverse('Home'))

def login(request):
	# If user already logged in, redirect to the Global Stream 
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	if request.method != 'POST':
		return 

	context = {} 
	form = LoginForm(request.POST)
	context['loginForm'] = form

	if not form.is_valid():
		context['reqistrationForm'] = RegistrationForm()
		return render(request, 'doMe/landing.html', context)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)
	return redirect(reverse('Home'))

@login_required
def home(request): 
	context = { 'workspaces': [w for w in request.user.profile_set.first().workspaces.all()], 'workspaceForm': LoginForm() }
	return render(request, 'doMe/home.html', context)

@login_required 
def logout(request):
	auth_logout(request)
	return redirect(reverse('Landing Page'))

def about(request):
	context = {}
	return render(request, 'doMe/about.html', context)