from django.urls import path
from . import views

app_name="employee"

urlpatterns = [
	path('', views.HomeView.as_view(), name="home"),
	path('about_us/', views.AboutUsView.as_view(), name="about_us"),
	path('employees/', views.EmployeeListView.as_view(), name="list"),
	path('employees/<slug:name>/', views.EmployeeDetailView.as_view(), name="detail"),
	path('schedule/', views.ScheduleView.as_view(), name="schedule"),
	path('admin/appointment', views.AppointmentAdminView.as_view(), name="appointment_admin"),

	path('ajax-get-employees/', views.ajax_get_employees, name="ajax_get_employees"),	
	path('ajax-get-dates/', views.ajax_get_dates, name="ajax_get_dates"),
	path('ajax-get-appts/', views.ajax_get_appts, name="ajax_get_appts"),


]