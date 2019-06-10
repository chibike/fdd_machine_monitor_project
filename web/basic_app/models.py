from django.contrib.auth.models import User
from django.db import models
import datetime
import json

class Device(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, help_text='Device id')
    read_pipe = models.CharField(max_length=1000, help_text='Read pipe for device', default="0xc2c2c2c2c2")
    write_pipe = models.CharField(max_length=1000, help_text='Write pipe for device', default="0xe7e7e7e7e7")

    def __str__(self):
        return "Device {}".format(self.id)

class MachineUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    time_on = models.DateTimeField(default=datetime.datetime.now, blank=True)
    time_off = models.DateTimeField(default=datetime.datetime.now, blank=True)
    total_time = models.DurationField()