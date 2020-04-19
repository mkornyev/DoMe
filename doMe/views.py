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
		return redirect(reverse('Landing Page'))

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
		return redirect(reverse('Landing Page'))

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

# ************************************************************
# 							HOME VIEW 		 				#
# ************************************************************

@login_required
def home(request): 
	context = createHomeContext(request)
	return render(request, 'doMe/home.html', context)

def createHomeContext(request):
	context = {}
	context['passedInForm'] = WorkspaceForm()
	context['title'] = 'My workspaces'
	context['pageType'] = 'Workspace'
	context['createFunction'] = 'createWorkspace'
	context['workspaces'] = Workspace.objects.filter(members=request.user)
	context['users'] = User.objects.exclude(id=request.user.id)

	return context

@login_required
def searchWorkspace(request):
	context = createHomeContext(request)
	context['clickJoin'] = "defaultOpen"
	if request.method != 'POST' or 'search' not in request.POST or not request.POST['search'].isdigit():
		context['modalError'] = 'invalid search query'
	else:
		context['search'] = request.POST['search']
		try: 
			workspace = Workspace.objects.get(id=int(request.POST['search']))
			context['workspaceQuery'] = workspace
		except: 
			context['modalError'] = 'invalid search query: workspace id doesn\'t exist'
	return render(request, 'doMe/home.html', context)
	
@login_required
def requestJoin(request):
	context = createHomeContext(request)
	if request.method != 'POST' or 'workspaceId' not in request.POST or not request.POST['workspaceId'].isdigit():
		context['error'] = 'invalid join request'
	else:
		context['joinMessage'] = "Request Sent!"
		workspace = Workspace.objects.get(id=int(request.POST['workspaceId']))
		workspace.requests.add(request.user)
	return render(request, 'doMe/home.html', context)
	

@login_required
def createWorkspace(request):
	if request.method != 'POST':
		return redirect(reverse('Landing Page'))

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

@login_required
def searchMembers(request):
	for item in request.POST:
		print(item)

# ************************************************************
# 							WORKSPACE View 		 				#
# ************************************************************

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
	context['requests'] = workspace.requests.all()
	context['count'] = workspace.members.count
	context['createFunction'] = 'createDoMeList'
	context['pageType'] = 'doMe List'
	context['itemForm'] = WorkspaceItemForm()
	return context

@login_required
def createDoMeList(request):
	if request.method != 'POST':
		redirect(reverse('Landing Page'))

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
	if request.method != 'POST' or 'dueDate' not in request.POST:
		return 

	form = WorkspaceItemForm(request.POST)
	try: 
		date = datetime.strptime(request.POST['dueDate'], '%d/%m/%Y %H:%M')
	except: 
		context = createViewWorkspaceContext(request, request.POST['workspaceId'])
		context['error']= 'Invalid Date'
		return render(request, 'doMe/home.html', context)

	if not form.is_valid():
		context = createViewWorkspaceContext(request, request.POST['workspaceId'])
		context['error']= 'Invalid Date'
		return render(request, 'doMe/home.html', context)
	else:
		current = get_object_or_404(List, id=request.POST['doMeListId'])

		newItem = Item(title=form.cleaned_data['title'], 
						description=form.cleaned_data['description'],
						user = request.user,
						order = current.items.count(),
						priority = form.cleaned_data['priority'],
						dueDate = date)
		newItem.save()

		current.items.add(newItem)
	return redirect(reverse('getWorkspace', args = (request.POST['workspaceId'],)))

@login_required
def acceptJoin(request):
	if request.method!='POST' or 'decision' not in request.POST:
		redirect(reverse('Landing Page'))
	workspace = get_object_or_404(Workspace, id=request.POST['workspaceId'])
	newMember = get_object_or_404(User, username = request.POST['username'])
	if request.POST['decision'] == 'accept':		
		workspace.members.add(newMember)
	workspace.requests.remove(newMember)
	return redirect(reverse('getWorkspace', args = (request.POST['workspaceId'],)))


# ************************************************************
# 							List  		 				#
# ************************************************************

@login_required
def viewList(request, id):
	return getList(request,id)

@login_required
def viewListByPriority(request, id):
	print('a')
	return getList(request,id, 'priority')

@login_required
def viewListByDate(request, id):
	return getList(request,id,'date')


def getList(request, id, sortOrder='default'):
	currList = get_object_or_404(List, id=id)
	workspace = currList.workspace.first()

	if request.user not in workspace.members.all():
		raise Http404

	context = { 'list': currList, 'itemForm': ItemForm(), 'id':id} 
	if sortOrder == 'default':
		context['items'] = currList.items.all()
	elif sortOrder == 'priority':
		context['items'] = currList.items.order_by('priority')
	elif sortOrder == 'date':
		context['items'] = currList.items.order_by('dueDate')
	# context[sortOrder] == 'active'
	return render(request, 'doMe/viewList.html', context)



@login_required
def addItem(request):
	# 'description' not in request.POST or 'dueDate' not in request.POST or 
	if request.method != 'POST' or 'listId' not in request.POST:
		return redirect(reverse('Landing Page'))
	
	currList = get_object_or_404(List, id=request.POST['listId'])	
	form = ItemForm(request.POST)

	try: 
		date = datetime.strptime(request.POST['dueDate'], '%d/%m/%Y %H:%M')
	except: 
		context = { 'list': currList, 'items': currList.items.all(), 'itemForm': form } 
		context['error']= 'Invalid Date'
		return render(request, 'doMe/home.html', context)

	if not form.is_valid() or date == None:
		redirect(reverse('getList', args=(request.POST['listId'],)))

	item = Item(user=request.user, 
				order=currList.items.count(), 				
				priority=form.cleaned_data['priority'], 
				title=form.cleaned_data['title'], 
				dueDate=date, 
				description=request.POST['description'])

	item.save() 
	currList.items.add(item)

	return redirect(reverse('getList', args=(request.POST['listId'],)))
	

# @login_required
# def createDoMeItem(request):
# 	if request.method != 'POST':
# 		return 

# 	form = ItemForm(request.POST)

# 	if not form.is_valid():
# 		context = createViewWorkspaceContext(request, request.POST['workspaceId'])
# 		context['error']= 'Invalid Date'
# 		return render(request, 'doMe/home.html', context)
# 	else:
# 		newItem = Item(title=form.cleaned_data['title'], 
# 						description=form.cleaned_data['description'],
# 						user = request.user,
# 						priority = form.cleaned_data['priority'],
# 						dueDate = form.cleaned_data['dueDate'])
# 		newItem.save()

# 		current = get_object_or_404(List, id=request.POST['doMeListId'])
# 		current.items.add(newItem)
# 	return redirect(reverse('getWorkspace', args = (request.POST['workspaceId'],)))
