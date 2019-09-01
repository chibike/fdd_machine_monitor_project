from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import json, os, time
import datetime
import shutil
import random

import gspread
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials

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


class GoogleSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=100, null=False)
    credentials = models.FileField(upload_to="uploads/%Y/%m/%d/")

    scope = ['https://spreadsheets.google.com/feeds']

    def sync(self):

        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials.path, self.scope)
        
        try:
            client = gspread.authorize(creds)
        except oauth2client.client.HttpAccessTokenRefreshError as e:
            print ("***** AUTH ERROR: `{}`".format(e))
            return False

        try:
            sheet = client.open(self.filename).sheet1
            print (dir(sheet))
        except gspread.exceptions.APIError as e:
            print ("***** IO ERROR: `{}`".format(e))
            return False

        return True


@receiver(models.signals.post_delete, sender=GoogleSheet)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    '''
        Deletes file from filesystem when corresponding Mediafile object is removed
    '''

    if instance.credentials:
        if os.path.isfile(instance.credentials.path):
            os.remove(instance.credentials.path)

            # remove folder if empty
            dir_name = os.path.abspath(os.path.join(instance.credentials.path, os.pardir))
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                if not os.listdir(dir_name):
                    try:
                        os.rmdir(dir_name)
                    except OSError: # path is not empty
                        # to force delete
                        # shutil.rmtree(dir_name)
                        pass


@receiver(models.signals.pre_save, sender=GoogleSheet)
def auto_delete_file_on_change(sender, instance, **kwargs):
    '''
        Deletes old file from filesystem when corresponding Mediafile object is updated with a new file
    '''

    if not instance.pk:
        return False
    
    try:
        old_file = sender.objects.get(pk=instance.pk).credentials
    except sender.DoesNotExist:
        return False
    
    new_file = instance.credentials
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

            # remove folder if empty
            dir_name = os.path.abspath(os.path.join(old_file.path, os.pardir))
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                if not os.listdir(dir_name):
                    try:
                        os.rmdir(dir_name)
                    except OSError: # path is not empty
                        # to force delete
                        # shutil.rmtree(dir_name)
                        pass