# Imports 
import os, json

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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
	homeList = List(isGlobal=True, title='New List', description='See all your toDos here')
	homeList.save()

	item = Item(user=user, title='Add a new goal!', description='And a goal description...', order=0)
	item.save()
	homeList.items.add(item)

	workspace = Workspace(organization='Home', description='Your new workspace.', admin=user)
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

	query = request.GET.get('query')
	workspace = request.GET.get('workspace')
	if query and workspace:
		users = User.objects.exclude(id=request.user.id).filter( Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query))
		workspaceObject = get_object_or_404(Workspace, id=workspace)
		context['users'] = [ u for u in users if u not in workspaceObject.members.all() ]
		context['openedModal'] = workspace

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
def searchUsers(request):
	context = createHomeContext(request)
	context['clickUsers'] = "defaultOpen"
	if request.method != 'POST' or 'search' not in request.POST:
		context['modalError'] = 'invalid search query'
	else:
			context['search'] = request.POST['search']
			workspaceObject = get_object_or_404(Workspace, id=request.POST['workspaceId'])
			users = User.objects.exclude(id=request.user.id).filter( Q(first_name__icontains=context['search']) | Q(last_name__icontains=context['search']) | Q(username__icontains=context['search']))
			context['users'] = [ u for u in users if u not in workspaceObject.members.all() ]
			print(context['users'])
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
def acceptJoin(request):
	if request.method!='POST' or 'decision' not in request.POST:
		redirect(reverse('Landing Page'))
	workspace = get_object_or_404(Workspace, id=request.POST['workspaceId'])
	newMember = get_object_or_404(User, username = request.POST['username'])
	workspace.members.add(newMember)
	workspace.requests.remove(newMember)
	return redirect(reverse('getWorkspace', args = (request.POST['workspaceId'],)))

@login_required
def leaveWorkspace(request):
	if request.method == "POST" and 'workspace' in request.POST and 'member' in request.POST: 
		workspace = get_object_or_404(Workspace, id=request.POST['workspace'])
		member = get_object_or_404(User, id=request.POST['member'])

		if request.user != member and request.user != workspace.admin:
			raise Http404

		workspace.members.remove(member)

		# Remove the workspace if there are no members left
		if workspace.members.all().count() == 0: 
			workspace.delete()
			
	return redirect(reverse('Home'))

@login_required
def addToWorkspace(request):
	if request.method == 'POST' and 'workspace' in request.POST and 'member' in request.POST: 
		workspace = get_object_or_404(Workspace, id=request.POST['workspace'])
		member = get_object_or_404(User, id=request.POST['member'])
		workspace.members.add(member)

		subject = "DoMe: You've been added to a new workspace."
		html_message = render_to_string('doMe/mailerNotification.html', {'workspace': workspace, 'member': member, 'admin': request.user })
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		
		mail.send_mail(subject, plain_message, from_email, [member.email], html_message=html_message, fail_silently=True)
		
	return redirect(reverse('Home'))


# ************************************************************
# 							Lists & Items  		 			 #
# ************************************************************

@login_required
def viewList(request, id):
	currList = get_object_or_404(List, id=id)
	workspace = currList.workspace.first()

	if request.user not in workspace.members.all():
		raise Http404

	context = { 'list': currList, 'items': currList.items.all(), 'itemForm': ItemForm() } 
	return render(request, 'doMe/viewList.html', context)

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
	return getList(request,id, 'priority')

@login_required
def viewListByDate(request, id):
	return getList(request,id,'date')

def getList(request, id, sortOrder='default'):
	currList = get_object_or_404(List, id=id)
	workspace = currList.workspace.first()

	if request.user not in workspace.members.all():
		raise Http404

	context = { 'list': currList, 'itemForm': ItemForm(), 'id':id, 'workspaceId': workspace.id}
	if sortOrder == 'default':
		context['items'] = currList.items.all()
	elif sortOrder == 'priority':
		context['items'] = currList.items.order_by('priority')
	elif sortOrder == 'date':
		context['items'] = currList.items.order_by('dueDate')
	context[sortOrder] = 'active'
	# context['active'] = sortOrder
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
	
@login_required
def updateItem(request):
	if request.method != "POST" or "id" not in request.POST or "to" not in request.POST: 
		return HttpResponse(json.dumps({ 'error': 'Missing field' }), content_type='application/json')

	item = get_object_or_404(Item, id=request.POST['id'])
	item.order = request.POST['to']
	item.save()

	return HttpResponse(json.dumps({ 'success': 'true' }), content_type='application/json')

@login_required
def deleteComplete(request):
	if request.method != 'POST':
		return redirect(reverse('Landing Page'))
	item = get_object_or_404(Item, id=request.POST['item'])
	l = get_object_or_404(List, id=request.POST['list'])
	if request.POST['action'] == 'delete':
		l.items.remove(item)
	elif request.POST['action'] =='complete':
		print(item.done)
		item.done = not item.done
		item.save()
		
	return redirect(reverse('getList', args=(l.id,)))	

# ************************************************************
# 							Users  		 				#
# ************************************************************


@login_required
def getProfile(request, id):
	user = get_object_or_404(User, id=id)
	itemCount = Item.objects.filter(user=user).count()

	context = { 'user': user, 'itemCount': itemCount }
	return render(request, 'doMe/profile.html', context)

@login_required
def getProfilePicture(request, id):
	user = get_object_or_404(User, id=id)

	if not user.profilePicture:
		raise Http404

	return HttpResponse(user.profilePicture, content_type=user.content_type)

@login_required
def editUser(request):
	context = {}
	user = get_object_or_404(User, id=request.user.id)
	oldImage = user.profilePicture
	form = UserForm(request.POST, request.FILES, instance=user)
	
	if not form.is_valid():
		context['form'] = form
		itemCount = Item.objects.filter(user=user).count()
		context = { 'user': user, 'itemCount': itemCount, 'form': form }
		return render(request, 'doMe/profile.html', context)
	else: 
		pic = form.cleaned_data['profilePicture']
		if pic and pic != '':

			# Update content type, remove old image
			try: 
				# Edge case where revalidated file is a FieldFile type (and not an Image)
				user.content_type = form.cleaned_data['profilePicture'].content_type

				if oldImage: 
					BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
					IMAGE_ROOT = os.path.join(BASE_DIR, 'doMe/user_uploads/' + oldImage.name)
					os.remove(IMAGE_ROOT)
			except: 
				pass
		form.save()

	return redirect(reverse('getProfile', args=(user.id,)))