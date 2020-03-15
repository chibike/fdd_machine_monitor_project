from django.contrib.auth.models import User
from django.db.models import Avg, Sum
from django.dispatch import receiver
from django.utils import timezone
import dateutil.relativedelta
from django.db import models
import json, os, time
import datetime
import shutil
import random

import gspread
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials

def get_default_time_window_datetime(delta=dateutil.relativedelta.relativedelta(months=-1)):
    return datetime.datetime.now() + delta

class UserWrapper(User):
    @staticmethod
    def get_users_usage_metrics(time_window=get_default_time_window_datetime()):
        users_usage_metrics = []
        
        for user in User.objects.all():
            metrics = {
                "id" : user.id,
                "label": user.username,
                "usage_metrics" : UserWrapper.get_usage_metrics(user, time_window)
            }

            users_usage_metrics.append(metrics)
        
        return users_usage_metrics

    @staticmethod
    def get_usage_metrics(user_reference, time_window=get_default_time_window_datetime()):
        usages = MachineUsage.objects.filter(user=user_reference).filter(device__state=True).filter(time_off__gte=time_window)
        usages = [round(usage.total_time.seconds/3600.0,4) for usage in usages]
        total = sum(usages)
        count = max(len(usages), 1)
        return {
            "usages": usages,
            "total" : total,
            "average" : round(total / count,4),
            "count" : count
        }

class ErrorCodes(object):
    # error codes
    UNAUTHORIZED = -1
    NOT_FOUND = -2
    FAILED_UPDATED = -3
    API_ERROR = -4
    UNKNOWN = -100

class Device(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, help_text='Device id')
    state = models.BooleanField(default=False)
    name = models.CharField(max_length=100, default="My Device")
    read_pipe = models.CharField(max_length=1000, help_text='Read pipe for device', default="0xc2c2c2c2c2")
    write_pipe = models.CharField(max_length=1000, help_text='Write pipe for device', default="0xe7e7e7e7e7")

    @staticmethod
    def get_devices_usage_metrics(time_window=get_default_time_window_datetime()):
        devices_usage_metrics = []
        
        for device in Device.objects.all():
            metrics = {
                "id" : device.id,
                "label": device.name,
                "state" : device.state,
                "usage_metrics" : device.get_usage_metrics(time_window)
            }

            devices_usage_metrics.append(metrics)
        
        return devices_usage_metrics

    def get_usage_metrics(self, time_window=get_default_time_window_datetime()):
        usages = MachineUsage.objects.filter(device=self).filter(device__state=True).filter(time_off__gte=time_window)
        usages = [round(usage.total_time.seconds/3600.0,4) for usage in usages]
        total = sum(usages)
        count = max(len(usages), 1)
        return {
            "usages" : usages,
            "total" : total,
            "average" : round(total / count,4),
            "count" : count
        }

    def __str__(self):
        return "Device {}: {}".format(self.id, self.name)
    
    def __repr__(self):
        return "Device {}: {}".format(self.id, self.name)


class MachineUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    time_on = models.DateTimeField(default=datetime.datetime.now, blank=True)
    time_off = models.DateTimeField(default=datetime.datetime.now, blank=True)
    total_time = models.DurationField()

    def update_gsheet(self):
        for gsheet in GoogleSheet.objects.filter(user=self.user):
            gsheet.update_sheet_with(self)


class GoogleSheetStatus(object):
    inactive = '-'
    should_sync = 'x'
    active = 'v'

    choices = [
        (inactive, 'In Active'),
        (should_sync, 'Sync'),
        (active, 'Active'),
    ]

    @staticmethod
    def get_default_choice():
        return GoogleSheetStatus.inactive


class GoogleSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    filename = models.CharField(max_length=100, null=False)
    credentials = models.FileField(upload_to="uploads/%Y/%m/%d/")
    has_header = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=GoogleSheetStatus.choices, default=GoogleSheetStatus.get_default_choice())

    scope =  ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    headers = ['User', 'Device', 'Time on', 'Time off', 'Duration']

    def update_status(self, status=GoogleSheetStatus.should_sync):
        self.status = status
        self.save()

    def authorize(self):
        client = None
        error_codes = []
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials.path, self.scope)
        try:
            client = gspread.authorize(creds)
        except oauth2client.client.HttpAccessTokenRefreshError as e:
            print ("***** AUTH ERROR: `{}`".format(e))
            error_codes.append(ErrorCodes.UNAUTHORIZED)
        except Exception as e:
            print ("Unknown error: `{}`".format(e))
            error_codes.append(ErrorCodes.UNKNOWN)
        
        return client, error_codes
    
    def get_gsheet(self):
        sheet = None
        client, error_codes = self.authorize()

        if client is not None:
            try:
                sheet = client.open(self.filename).sheet1
                self.update_status(GoogleSheetStatus.should_sync)
            except gspread.exceptions.SpreadsheetNotFound:
                print ("SpreadsheetNotFound error: `{}`".format(e))
                error_codes.append(ErrorCodes.NOT_FOUND)
            except gspread.exceptions.APIError:
                print ("APIError error: `{}`".format(e))
                error_codes.append(ErrorCodes.API_ERROR)
            except Exception as e:
                print ("Unknown error: `{}`".format(e))
                error_codes.append(ErrorCodes.UNKNOWN)
        else:
            error_codes.append(ErrorCodes.UNAUTHORIZED)
        
        return sheet, error_codes

    def sync(self):
        for deferred_submission in DeferredSubmission.objects.filter(gsheet=self):
            self.update_sheet_with(deferred_submission.machine_usage)
            deferred_submission.delete()

        return True
    
    @staticmethod
    def sync_all():
        for gsheet in GoogleSheet.objects.all():
            gsheet.sync()

        return True
    
    def update_sheet_with(self, machine_usage):

        def __perform_update(sheet, row):
            if isinstance(sheet, gspread.models.Worksheet):
                # perform better validation for append row
                return bool(sheet.append_row(row))
            return False
        
        def __defer_update():
            # TODO: Update gsheet status to indicate a defered data

            deferred_submission = DeferredSubmission(gsheet=self, machine_usage=machine_usage)
            deferred_submission.save()
            return True


        sheet, error_codes = self.get_gsheet()
        if (ErrorCodes.UNAUTHORIZED in error_codes) or (ErrorCodes.NOT_FOUND in error_codes):
            if not __defer_update():
                error_codes.append(ErrorCodes.FAILED_UPDATED)
        elif len(error_codes) <= 0 and sheet is not None:
            row = [
                str(machine_usage.user.username),
                str(machine_usage.device),
                str(machine_usage.time_on),
                str(machine_usage.time_off),
                str(machine_usage.total_time),
            ]

            if not self.has_header:
                '''
                    Adds the column headers for the spread sheet
                '''
                #sheet.insert_row(self.headers, 1)
                self.has_header = True
                self.save()

            if not __perform_update(sheet, row):
                error_codes.append(ErrorCodes.FAILED_UPDATED)
            else:
                if len(DeferredSubmission.objects.filter(gsheet=self)) <= 0:
                    self.update_status(GoogleSheetStatus.active)
                else:
                    self.update_status(GoogleSheetStatus.should_sync)
        
        return len(error_codes) <= 0
    

class DeferredSubmission(models.Model):
    machine_usage = models.ForeignKey(MachineUsage, on_delete=models.CASCADE, null=False)
    gsheet = models.ForeignKey(GoogleSheet, on_delete=models.CASCADE, null=False)



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


@receiver(models.signals.post_save, sender=MachineUsage)
def update_google_sheets(sender, instance, **kwargs):
    '''
        Updates linked google sheets
    '''

    instance.update_gsheet()
