from django.contrib import admin
from basic_app.models import Device, MachineUsage, GoogleSheet, DeferredSubmission

# Register your models here.
admin.site.register(Device)
admin.site.register(MachineUsage)
admin.site.register(GoogleSheet)
admin.site.register(DeferredSubmission)
