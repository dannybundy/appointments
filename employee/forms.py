from django import forms
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from dateutil import parser
from dateutil.relativedelta import *

from datetime import datetime
import pytz

from phonenumber_field.phonenumber import PhoneNumber
from twilio.rest import Client
from crispy_forms.helper import FormHelper
import random, string
import re

from .models import Employee, Customer, Appointment, Service


# Gets rid of whitespace
class CustomCharField(forms.CharField):
	def clean(self, value):
		if value:
			return ' '.join(value.split())
		return None


class PhoneNumberForm(forms.Form):
	country_code = CountryField().formfield(
		required=False, initial='US', widget=CountrySelectWidget(
			attrs={
				'class':'form-control',
				'aria-describedby':'number-addon',
				'style':'width:0px; display:inline-block'
			}
		)
	)
	area_code = CustomCharField(
		required=False, max_length=5, widget=forms.TextInput(
			attrs={
				'placeholder':'626', 'class':'form-control',
				'style':'width:60px; display:inline-block'
			}
		)
	)
	number = CustomCharField(
		required=False, max_length=15, widget=forms.TextInput(
			attrs={
				'placeholder':'3982102', 'class':'form-control',
				'style':'width:100px; display:inline-block'
			}
		)
	)

	phonenumber = CustomCharField(required=False, max_length=0)

	def clean_phonenumber(self):
		clean = self.cleaned_data
		country_code = clean.get('country_code')
		area_code = clean.get('area_code')
		number = clean.get('number')

		if (area_code or number):
			if not (area_code and number):
				raise forms.ValidationError("Please fill in blank fields.")
		else:
			return None

		if re.search('[a-zA-Z]', area_code) or re.search('[a-zA-Z]', number):
			raise forms.ValidationError("The phone number entered is not valid.")

		whole_phone = PhoneNumber.from_string(
			phone_number=f"{area_code}{number}", region=country_code
		).as_e164

		return whole_phone


account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN
class CustomerForm(PhoneNumberForm, forms.ModelForm):
	customer_info = CustomCharField(required=False, widget=forms.Textarea())
	email = forms.EmailField(max_length=50)

	class Meta:
		model = Customer
		fields= (
			'name',
			'email',
			'country_code',
			'area_code',
			'number',
			'phonenumber',
			'customer_info',
		)

	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request

		self.helper = FormHelper()
		self.helper.form_show_labels = False

	def send_emails(self, appointment):
		converted_date = timezone.localtime(appointment.date)
		time = converted_date.strftime("%I:%M %p")

		# html_customer_email = render_to_string(
		# 	'employee/scheduled_customer_email.html',
		# 	{'appointment': appointment,}
		# )

		customer_email = f"""
			Hi {appointment.customer.name}, you've scheduled a {time} 
			appointment with {appointment.employee.name}. Make sure you're here 10 minutes 
			early. If you do decide to cancel or change your appointment, please 
			do so a day in advanced. Thanks and we'll see you soon!)
			"""
		customer_email = ' '.join(customer_email.split())
		
		send_mail(
			'Business Name: Appointment Scheduled',
			customer_email,
			'readapt-barber@readapt.com',
			['pilotdk13@gmail.com',],
			fail_silently=False,
			# html_message=html_customer_email,
		)


		# html_business_email = render_to_string(
		# 	'employee/scheduled_business_email.html',
		# 	{'appointment': appointment,}
		# )
		send_mail(
			'Business Name: Appointment Scheduled',
			f"""{appointment.employee.name} has a {time} appointment with {appointment.customer.name}.""",
			'readapt-barber@readapt.com',
			['pilotdk13@gmail.com'],
			fail_silently=False,
			# html_message=html_business_email,
		)

		messages.success(
			self.request,
			"""Appointment has been scheduled! Check your email
			for appointment details.
			"""
		)

		return 'Emails were sent'

	def send_text(self, appointment):
		converted_date = timezone.localtime(appointment.date)
		time = converted_date.strftime("%I:%M %p")

		customer = appointment.customer
		if customer.phonenumber is not None:
			customer_text = f"""
			Hi {appointment.customer.name}, you've scheduled a {time} 
			appointment with {appointment.employee.name}. Make sure you're 
			here 10 minutes early. If you do decide to cancel or change your appointment, please 
			do so a day in advanced. Thanks and we'll see you soon! - Business Name
			"""
			customer_text = ' '.join(customer_text.split())

			client = Client(account_sid, auth_token)
			client.messages.create(
				to=str(customer.phonenumber),
				from_=settings.TRIAL_NUMBER,
				body=customer_text,
			)
			messages.success(
				self.request,
				"Appointment has been scheduled! We've sent you a text with details."
			)

			return 'Text was sent'

		return 'Text was not sent'

	def save(self):
		clean = self.cleaned_data
		post = self.request.POST

		customer = Customer.objects.get_or_create(
			name=clean.get('name'),
			email=clean.get('email')
		)[0]

		appt_pk = post['appt_pk']
		appt = Appointment.objects.get(pk=appt_pk)

		if customer.phonenumber!=clean.get('phonenumber'):
			customer.phonenumber = clean.get('phonenumber')
			customer.save()

		service_pk = post['service_pk']
		if service_pk:
			service = Service.objects.get(pk=service_pk)
			appt.service = service

		appt.customer = customer
		appt.customer_info = self.cleaned_data.get('customer_info')
		appt.scheduled = True
		appt.save()

		# self.send_emails(appt)
		# self.send_text(appt)

		return customer


"""
Keep 'date_options()' and 'time_options()' in local time. Will convert
to utc time in 'AdminAppointmentForm' function 'create_appointments()'
 """

def date_options():
	start_date = timezone.localtime(timezone.now())
	end_date = start_date + relativedelta(months=+3)

	DATE_LIST = []
	date = start_date

	while date < end_date:
		date_str = date.strftime('%B %d, %Y - %A')
		DATE_LIST.append([date, date_str])
		date = date + relativedelta(days=+1)

	return DATE_LIST

def time_options():
	start_time = timezone.localtime(timezone.now()).replace(hour=8, minute=0, second=0)
	end_time = start_time + relativedelta(hours=+10)

	TIME_LIST = []
	date = start_time

	while date < end_time:
		date_str = date.strftime('%I:%M %p')
		TIME_LIST.append([date, date_str])
		date = date + relativedelta(minutes=+15)

	return TIME_LIST

def employee_options():
	EMPLOYEE_LIST = []
	
	for employee in Employee.objects.all():
		EMPLOYEE_LIST.append([employee.pk, employee.name])

	return EMPLOYEE_LIST

class AdminAppointmentForm(forms.Form):
	date_options = forms.MultipleChoiceField(
		choices=date_options(),
		widget=forms.SelectMultiple(
			attrs={'size':12}
		)
	)

	time_options = forms.MultipleChoiceField(
		choices=time_options(),
		widget=forms.SelectMultiple(
			attrs={'size':12}
		)
	)

	employee_options = forms.MultipleChoiceField(
		choices=employee_options(),
		widget=forms.SelectMultiple(
			attrs={'size':6}
		)
	)

	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request

		self.helper = FormHelper()
		self.helper.form_show_labels = False

	def create_appointments(self):
		day_list = self.request.POST.getlist('date_options')
		time_list = self.request.POST.getlist('time_options')
		employee_pk_list = self.request.POST.getlist('employee_options')
	
		if len(day_list)>0 and len(time_list)>0 and len(employee_pk_list)>0:

			for pk in employee_pk_list:
				employee = Employee.objects.get(pk=pk)

				for day in day_list:
					day = parser.parse(day).date()

					for time in time_list:
						time = parser.parse(time).time()						
						date_as_utc = datetime.combine(day, time).astimezone(pytz.utc)

						Appointment.objects.create(
							employee=employee,
							date=date_as_utc
						)

			messages.success(self.request, "Appointments were created!")
			return 'Appointments were created'

		return 'No appointments were created'