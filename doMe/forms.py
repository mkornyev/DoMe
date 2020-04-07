# IMPORTS

from datetime import datetime

from django import forms
from django.contrib.auth import authenticate
from django.db import models
from doMe.models import *

INPUT_ATTRIBUTES = {'class' : 'form-input form-control'}
MAX_UPLOAD_SIZE = 2500000


class LoginForm(forms.Form):
	username = forms.CharField(max_length = 50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password = forms.CharField(max_length = 50, widget=forms.PasswordInput(attrs=INPUT_ATTRIBUTES))

	def clean(self):
		cleaned_data = super().clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')

		user = authenticate(username=username, password=password)

		if not user:
			raise forms.ValidationError("Invalid Username or Password Entered")

		return cleaned_data

class RegistrationForm(forms.Form):
	username   = forms.CharField(max_length = 50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password  = forms.CharField(max_length = 50, label='Password', widget = forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	confirm_password  = forms.CharField(max_length = 50, label='Confirm Password', widget = forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	email      = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')

		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError("Passwords did not match.")

		return cleaned_data

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		return username
		
	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if len(cleaned_phone) != 10:
			raise forms.ValidationError('You must enter a valid phone number')

		return cleaned_phone

# MODEL FORMS

class WorkspaceForm(forms.Form):
	organization = forms.CharField(max_length = 50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	description = forms.CharField(max_length = 200, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	# def clean_organization(self):
	# 	organization = self.cleaned_data.get('organization')
	# 	if Workspace.objects.filter(organization__exact=organization):
	# 		raise forms.ValidationError("Organization already exists.")

	# 	return organization

class ListForm(forms.Form):
	title = forms.CharField(max_length = 40, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	description = forms.CharField(max_length = 100, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	def clean(self):
		cleaned_data = super().clean()
		description = cleaned_data.get('description')
		return cleaned_data

	# Unique title, but only within a workspace

class ItemForm(forms.Form):
	priority = forms.CharField(widget=forms.Select(choices=Priority.choices, attrs={'class':'form-input form-select'}))
	title = forms.CharField(max_length=30, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# dueDate = forms.DateTimeField(label='Due Date ',
    #     input_formats=['%d/%m/%Y %H:%M'],
    #     widget=forms.DateTimeInput(attrs={
    #         'class': 'form-control datetimepicker-input',
    #         'data-target': '#datetimepicker'
    #     })
    # )
    
# 	description = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
# 	dueDate = forms.DateField(label = 'Due date', widget=forms.TextInput(attrs=INPUT_ATTRIBUTES),initial=datetime.now().date())

	def clean_dueDate(self):
		dueDate = self.cleaned_data.get('dueDate')
		if dueDate < datetime.now().date():
			raise forms.ValidationError("Due Date must be in the future.")
		return dueDate
	
	# def clean_priority(self):
	# 	priority = self.cleaned_data.get('priority')
	# 	if priority not in [1, 2, 3]:
	# 		raise forms.ValidationError("Must have a valid priority")

	# 	return priority
