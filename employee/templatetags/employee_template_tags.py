from django import template
from django.utils import timezone
import calendar

register = template.Library()

@register.filter
def month_name(month_number):
	return calendar.month_name[month_number]

@register.filter
def localize_time(day):
	time = timezone.localtime(day)
	time = time.strftime('%I:%M %p')
	return time