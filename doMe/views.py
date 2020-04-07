# Imports 

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from doMe.forms import *
from doMe.models import *


# BASIC VIEWS

def landingPage(request):
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	context = {} 
	context['loginForm'] = LoginForm()
	context['loginTab'] = 'defaultOpen'
	context['registrationForm'] = RegistrationForm()
	return render(request, 'doMe/landing.html', context)

def register(request):
	if request.method != 'POST':
		return 

	context = {}
	context['registrationForm'] = RegistrationForm(request.POST)

	form = RegistrationForm(request.POST)

	if not form.is_valid():
		context['registerTab'] = 'defaultOpen'
		context['loginForm'] = LoginForm()
		return render(request, 'doMe/landing.html', context)

	user = User.objects.create_user(username=form.cleaned_data['username'], 
										password=form.cleaned_data['password'],
										email=form.cleaned_data['email'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])

	user.save()
	
	# Default user workspace setup
	homeList = List(isGlobal=True, title='Global List', description='See all your toDos here')
	homeList.save()

	item = Item(user=user, title='Add a new goal!', description='And a goal description...')
	item.save()
	homeList.items.add(item)

	workspace = Workspace(organization='Home', description='Your private workspace.', admin=user)
	workspace.save()
	workspace.members.add(user) 
	workspace.lists.add(homeList)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)

	return redirect(reverse('Home'))

def login(request):
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	if request.method != 'POST':
		return 

	context = {} 
	form = LoginForm(request.POST)
	context['loginForm'] = form

	if not form.is_valid():
		context['registrationForm'] = RegistrationForm()
		context['loginTab'] = 'defaultOpen'
		return render(request, 'doMe/landing.html', context)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)
	return redirect(reverse('Home'))

@login_required 
def logout(request):
	auth_logout(request)
	return redirect(reverse('Landing Page'))

def about(request):
	context = {}
	return render(request, 'doMe/about.html', context)

@login_required
def home(request): 
	context = createHomeContext(request)
	return render(request, 'doMe/home.html', context)

def createHomeContext(request):
	context = {}
	context['passedInForm'] = WorkspaceForm()
	context['title'] = 'My workspaces'
	context['pageType'] = 'workspace'
	context['createFunction'] = 'createWorkspace'
	context['workspaces'] = Workspace.objects.filter(members=request.user)

	return context


# WORKSPACES

@login_required
def viewWorkspace(request, id):
	context = createViewWorkspaceContext(request, id)
	return render(request, 'doMe/home.html', context)

def createViewWorkspaceContext(request, id): 
	workspace = get_object_or_404(Workspace, id=id)

	context = {}
	context['passedInForm'] = ListForm()
	context['workspaceId'] = workspace.id
	context['lists'] = workspace.lists.all()
	context['title'] = workspace.organization
	context['createFunction'] = 'createDoMeList'
	context['pageType'] = 'doMe List'
	context['itemForm'] = ItemForm()
	return context

@login_required
def createWorkspace(request):
	if request.method != 'POST':
		return 

	form = WorkspaceForm(request.POST)
	if not form.is_valid():
		context = createHomeContext(request)
		context['error']= 'Organization name taken'
		return render(request, 'doMe/home.html', context)
	else:
		workspace = Workspace(organization=form.cleaned_data['organization'], 
								description=form.cleaned_data['description'],
								admin = request.user)
		workspace.save()
		workspace.members.add(request.user)

	return redirect(reverse('Home'))


# LISTS

@login_required
def createDoMeList(request):
	if request.method != 'POST':
		return 

	form = ListForm(request.POST)

	if not form.is_valid():
		context = createViewWorkspaceContext(request, request.POST['workspaceId'])
		context['error']= 'List name taken'
		return render(request, 'doMe/home.html', context)
	else:
		newList = List(title=form.cleaned_data['title'], description=form.cleaned_data['description'])
		newList.save()

		workspace = get_object_or_404(Workspace, id=request.POST['workspaceId'])
		workspace.lists.add(newList)
	return redirect(reverse('getWorkspace', args = (workspace.id,)))

@login_required
def createDoMeItem(request):
	if request.method != 'POST':
		return 

	form = ItemForm(request.POST)

	if not form.is_valid():
		context = createViewWorkspaceContext(request, request.POST['workspaceId'])
		context['error']= 'Invalid Date'
		return render(request, 'doMe/home.html', context)
	else:
		newItem = Item(title=form.cleaned_data['title'], 
						description=form.cleaned_data['description'],
						user = request.user,
						priority = form.cleaned_data['priority'],
						dueDate = form.cleaned_data['dueDate'])
		newItem.save()

		current = get_object_or_404(List, id=request.POST['doMeListId'])
		current.items.add(newItem)
	print('***', request.POST)
	print('**', request.POST['workspaceId'])
	return redirect(reverse('getWorkspace', args = (request.POST['workspaceId'],)))

@login_required
def viewList(request, id):
	if request.method != 'POST' or not 'workspaceId' in request.POST:
		return 
	workspace = get_object_or_404(Workspace, id=request.POST['workspaceId'])
	list = get_object_or_404(List, id=id)

	if request.user not in workspace.members.all():
		raise Http404

	return render(request, 'doMe/home.html', context)
