from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from phonenumber_field.modelfields import PhoneNumberField

import pytz
from django.db import models
from timezone_field import TimeZoneField

from math import floor


class Service(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=100)
	length = models.IntegerField()
	price = models.IntegerField()

	def convert_length(self):
		hour_exp = floor(self.length/60)
		min_exp = floor(self.length%60)

		if hour_exp==0:
			hour = ''
		elif hour_exp==1:
			hour = f"{hour_exp} hr "
		else:
			hour = f"{hour_exp} hrs "

		if min_exp==0:
			minute = ''
		else:
			minute = f"{min_exp} min"

		return hour + minute
			

	def __str__(self):
		return f"{self.name} ({self.convert_length()}) - ${self.price}"


class Employee(models.Model):
	# user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)

	name = models.CharField(max_length=50)
	info = models.TextField()
	picture = CloudinaryField(blank=True, null=True)

	date_started = models.DateTimeField(default=timezone.now)
	slug = models.SlugField(unique=True)

	services = models.ManyToManyField(Service, blank=True)

	def save(self, *args, **kwargs):
		self.slug = self.slug or slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Showcase(models.Model):
	employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)

	title = models.CharField(max_length=50)
	info = models.CharField(max_length=50)
	img = CloudinaryField(blank=True, null=True)

	def __str__(self):
		return f"{self.employee.name}: {self.title}"




class Customer(models.Model):
	name = models.CharField(max_length=50)
	email = models.EmailField(max_length=50, blank=True)
	phonenumber = PhoneNumberField(null=True, blank=True)

	def __str__(self):
		return f"{self.name}"


class Appointment(models.Model):
	employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
	service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True)

	date = models.DateTimeField()
	customer_info = models.TextField(blank=True, null=True)
	extra_notes = models.TextField(blank=True, null=True)
	scheduled = models.BooleanField(default=False)
	completed = models.BooleanField(default=False)

	def __str__(self):
		converted_date = timezone.localtime(self.date) if self.date is not None else None
		time = converted_date.strftime("%I:%M %p")

		return f"{self.employee}: {time}"