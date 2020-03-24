from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	profilePicture = models.FileField(blank=True)

class Workspace(models.Model):
	members = models.ManyToManyField(Profile, related_name = "Users")
	description = models.CharField(max_length=200)
	listItems = models.ManyToManyField(toDoItem)

class toDoItem(models.Model):
	class Priority(models.IntegerChoices):
		High = 1
		Medium = 2
		Low = 3

	priority = models.IntegerField(choices = Priority.choices)
	done = models.BooleanField()
	user = models.ForeignKey(User)
	title = models.CharField(max_length=30)
	description = models.CharField(max_length=150)
	dueDate = models.DateTimeField()

