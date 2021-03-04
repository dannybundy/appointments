from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Avg

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models import Employee, Showcase, Appointment, Customer, Service


class ShowcaseInline(admin.StackedInline):
	model = Showcase
	extra = 0

class ShowcaseInline(admin.StackedInline):
	model = Showcase
	extra = 0

class EmployeeAdmin(admin.ModelAdmin):
	inlines = [ShowcaseInline]
	search_fields = (
		'name',
	)


class CustomerAdmin(admin.ModelAdmin):
	search_fields = (
		'name',
		'email',
		'phonenumber',
	)
	list_display = (
		'name',
		'email',
		'phonenumber',
	)


class CustomChangeList(ChangeList):
	def get_results(self, *args, **kwargs):
		super().get_results(*args, **kwargs)
		queryset = self.result_list.filter(completed=True).aggregate(
			appointment_sum=Sum('service__price')
		)
		self.appointment_total = queryset['appointment_sum']


# def completed_true(modeladmin, request, queryset):
# 	queryset.update(completed=True)

# completed_true.short_description = "Selected appointments have been completed"


class AppointmentAdmin(admin.ModelAdmin):
	def get_changelist(self, request):
		return CustomChangeList

	def formfield_for_dbfield(self, dbfield, *args, **kwargs):
		formfield = super().formfield_for_dbfield(dbfield, *args, **kwargs)
		if dbfield.name=='employee' or dbfield.name=='service' :
			formfield.widget.can_add_related = False
			formfield.widget.can_delete_related = False
			formfield.widget.can_change_related = False

		return formfield

	search_fields = (
		'employee__name',
		'customer__name',
		'customer__email',
		'customer__phonenumber',
		'service__name',
		'date',
	)
	list_display = (
		'date',
		'employee',
		'service',
		'customer',
		'scheduled',
		'completed'
	)
	list_editable = (
		'employee',
		'service',
		'customer',
		'completed',
		'scheduled',
	)
	list_filter = (
		'date',
		('date', DateRangeFilter),
		'employee',
	)


admin.site.unregister(Group)
admin.site.register(Service)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Appointment, AppointmentAdmin)