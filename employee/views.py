from django.views.generic import View, TemplateView, FormView, UpdateView, DetailView, ListView
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers
from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.contrib import messages

from django.utils import timezone
from datetime import datetime, time
from dateutil import parser
from dateutil.relativedelta import *

import pytz
import json

from .models import Employee, Showcase, Appointment, Service
from .forms import CustomerForm, AdminAppointmentForm


class HomeView(TemplateView):
	template_name = "employee/home.html"


class AboutUsView(TemplateView):
	template_name = "employee/about_us.html"


class EmployeeListView(ListView):
	model = Employee
	queryset = Employee.objects.order_by('name')
	template_name = "employee/employee_list.html"


class EmployeeDetailView(DetailView):
	model = Employee
	template_name = "employee/employee_detail.html"
	slug_field = 'slug'
	slug_url_kwarg = 'name'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['showcase_list'] = Showcase.objects.filter(employee=self.get_object())

		return context


class ScheduleView(FormView):
	template_name = "employee/schedule.html"
	form_class = CustomerForm
	success_url = reverse_lazy('employee:home')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		today = timezone.localtime(timezone.now())
		context['today'] = today.strftime('%B %d, %Y - %A')
		context['employee_list'] = Employee.objects.all()
		context['service_list'] = Service.objects.all()

		return context

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs.update({'request': self.request})
		return kwargs

	def post(self, *args, **kwargs):
		if self.request.is_ajax():
			self.request.POST = self.request.POST.copy()
			json_data = json.loads(self.request.POST['json_data'])[1:]

			data = {}
			for element in json_data:
				self.request.POST[element['name']] = element['value']

		return super().post(self.request, **kwargs)

	def form_valid(self, form):
		form.save()
		if self.request.is_ajax():
			url = reverse('employee:home')
			return JsonResponse({'url':url}, status=200)

		return super().form_valid(form)


	def form_invalid(self, form):
		context = {
			'url':None,
			'phonenumberError':form.errors['phonenumber']}

		return JsonResponse(context, status=200)


def ajax_get_employees(request):
	if request.is_ajax():
		service_pk = request.POST['service_pk']

		if service_pk:
			employee_list = Employee.objects.filter(services__pk=service_pk).order_by('name')
		else:
			employee_list = Employee.objects.all()

		json_array = []
		for employee in employee_list:
			json_appt = serializers.serialize('json', [employee,])
			json_array.append(json_appt)

		return JsonResponse({'employeeArray':json_array})

	return redirect('employee:schedule')


def ajax_get_dates(request):
	if request.is_ajax():
		now_as_local = timezone.localtime(timezone.now())
		morning = now_as_local.replace(hour=7, minute=0, second=0).time()	
		night = now_as_local.replace(hour=22, minute=0, second=0).time()

		appt_list = Appointment.objects.filter(
			scheduled=False,
			date__gte=now_as_local,
			date__time__gte=morning,
			date__time__lte=night,
		)

		service_pk = request.POST['service_pk']
		if service_pk:
			appt_list = appt_list.filter(employee__services__pk=service_pk)

		employee_pk = request.POST['employee_pk']
		if employee_pk:
			appt_list = appt_list.filter(employee__pk=employee_pk)


		date_str_list = []
		date_obj_list = appt_list.values('date')

		for date in date_obj_list:
			date_local = timezone.localtime(date['date'])
			date_str_list.append(date_local)

		date_str_list = list(set(date_str_list))

		return JsonResponse({'dateArray':date_str_list}, status=200)

	return redirect('employee:schedule')


# day in local time
def get_appts(day, employee_pk):
	morning = timezone.localtime(day).replace(hour=7, minute=0, second=0)
	afternoon = timezone.localtime(day).replace(hour=12, minute=0, second=0)
	evening = timezone.localtime(day).replace(hour=17, minute=0, second=0)
	night = timezone.localtime(day).replace(hour=22, minute=0, second=0)

	morning_appts = Appointment.objects.filter(
		scheduled=False,
		date__gte=morning,
		date__lte=afternoon
	)
	afternoon_appts = Appointment.objects.filter(
		scheduled=False,
		date__gte=afternoon,
		date__lte=evening
	)
	evening_appts = Appointment.objects.filter(
		scheduled=False,
		date__gte=evening,
		date__lte=night
	)

	if employee_pk:
		morning_appts = morning_appts.filter(employee__pk=employee_pk)
		afternoon_appts = afternoon_appts.filter(employee__pk=employee_pk)
		evening_appts = evening_appts.filter(employee__pk=employee_pk)


	appt_lists = [
		morning_appts,
		afternoon_appts,
		evening_appts,
	]

	json_array = []
	for appt_list in appt_lists:
		temp_array = []
		for appt in appt_list:
			json_appt = serializers.serialize('json', [appt,])
			temp_array.append(json_appt)
		json_array.append(temp_array)

	return json_array

def ajax_get_appts(request):
	if request.is_ajax():
		post_date = request.POST['date']
		date_obj = timezone.localtime(parser.parse(post_date).astimezone(pytz.utc))

		employee_pk = request.POST['employee_pk']
		if employee_pk:
			json_array = get_appts(date_obj, employee_pk)
		else:
			json_array =  get_appts(date_obj, None)

		return JsonResponse({'apptListArray':json_array}, status=200)

	return redirect('employee:schedule')


class AppointmentAdminView(FormView):
	template_name = "employee/appointment_admin.html"
	form_class = AdminAppointmentForm
	success_url = reverse_lazy('employee:appointment_admin')

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs.update({'request': self.request})
		return kwargs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		today = timezone.localtime(timezone.now())
		context['today'] = today.strftime('%B %d, %Y - %A')

		return context

	def form_valid(self, form):
		form.create_appointments()
		return super().form_valid(form)