from django.contrib import admin

# Register your models here.
from ippon.event_models import Event, EventAdmin


admin.site.register(Event)
admin.site.register(EventAdmin)
