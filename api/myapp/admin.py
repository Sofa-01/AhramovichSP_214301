from django.contrib import admin
from . import models

admin.site.register(models.Tour)
admin.site.register(models.Place)
admin.site.register(models.Hotel)
admin.site.register(models.TransportType)
admin.site.register(models.TransportPlace)
admin.site.register(models.TransportRoute)
admin.site.register(models.City)
