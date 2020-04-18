"""t33 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from doMe import views 

urlpatterns = [
    path('admin/', admin.site.urls),

    # Basic Routes
    path('', views.landingPage, name='Landing Page'),
    path('home/', views.home, name='Home'),
    path('login/', views.login, name = 'Login'),
    path('register/', views.register, name='Register'),
    path('logout/', views.logout, name='Logout'),
    path('about/', views.about, name='About'),

    # Page Views
    path('workspace/<int:id>', views.viewWorkspace, name='getWorkspace'),
    path('list/<int:id>', views.viewList, name='getList'),

    # Create
    path('createWorkspace', views.createWorkspace, name='createWorkspace'),
    path('createDoMeList', views.createDoMeList, name='createDoMeList'),

    path('list/<int:id>', views.viewList, name='getList'),
    path('addItem/', views.addItem, name='addItem'),
    path('createDoMeItem', views.createDoMeItem, name='createDoMeItem'),    

    path('requestJoin', views.requestJoin, name='requestJoin'),
    path('acceptJoin', views.acceptJoin, name='acceptJoin'),
    path('leaveWorkspace/', views.leaveWorkspace, name='leaveWorkspace'),    
    path('addToWorkspace/', views.addToWorkspace, name='addToWorkspace'),    

    path('searchMembers/', views.searchMembers, name='searchMembers'),    
    path('searchWorkspace/', views.searchWorkspace, name='searchWorkspace'),    

]
