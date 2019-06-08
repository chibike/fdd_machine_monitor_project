from django.contrib.auth.models import User
from django.db import models
import json

class Device(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, help_text='Device id')
    read_pipe = models.CharField(max_length=1000, help_text='Read pipe for device', default="0xc2c2c2c2c2")
    write_pipe = models.CharField(max_length=1000, help_text='Write pipe for device', default="0xe7e7e7e7e7")

    def __str__(self):
        return json.dumps({"read_pipe":self.read_pipe, "write_pipe":self.write_pipe, "id":self.id})