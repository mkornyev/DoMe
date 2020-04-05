# IMPORTS 

from datetime import datetime 

from django.db import models
from django.contrib.auth.models import AbstractUser

 
class User(AbstractUser):
	profilePicture = models.FileField(blank=True)
	# workspaces / workspaces_set
	
	def __str__(self):
		return self.get_username() + " (" + self.get_full_name() + ")"

	def print_attributes(self):
		print("---\nUsername: " + self.get_username() + "\nFirst name: " + self.first_name + "\nLast name: " + self.last_name + "\nEmail: " + self.email + "\nActive:" + str(self.is_active) + "\n---")

class Priority(models.IntegerChoices):
		High = 1
		Medium = 2
		Low = 3

class Item(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	# list / list_set

	priority = models.IntegerField(default=0, choices = Priority.choices)	
	order = models.IntegerField(default=0)	# Order within list
	done = models.BooleanField(default=False)
	title = models.CharField(max_length=30)
	description = models.CharField(max_length=150)
	dueDate = models.DateTimeField(blank=True, null=True)

class List(models.Model):
	items = models.ManyToManyField(Item, related_name='list')
	# workspace / workspace_set

	title = models.CharField(max_length=30, default='Your new toDo list')
	description = models.CharField(max_length=200, default='Add to me!')
	isGlobal = models.BooleanField(default=False) # Whether the List is the user's global list

class Workspace(models.Model):
	admin = models.ForeignKey(User, on_delete=models.PROTECT)
	members = models.ManyToManyField(User, related_name='workspaces')
	lists = models.ManyToManyField(List, related_name='workspace')

	organization = models.CharField(max_length=30, default='New Workspace')
	description = models.CharField(max_length=200)
	

