from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables
from django_tables2.tables import columns

from basic_app.models import Device, MachineUsage, GoogleSheet
import random

class UserTable(tables.Table):
    action = columns.Column(orderable=False, verbose_name='Action', empty_values=())
    id = columns.Column(verbose_name='#')
    # is_superuser = columns.Column(verbose_name='Superuser')

    @staticmethod
    def render_is_superuser(record):
        if record.is_superuser:
            return format_html('<img class="icon" src="{0}" alt="has certificate"', static('vendor/open-iconic/svg/check.svg'))
        return format_html('<img class="icon" src="{0}" alt="no certificate"', static('vendor/open-iconic/svg/x.svg'))

    @staticmethod
    def render_action(record):
        return format_html('''<a href="#" class="delete_tag"
                  data-toggle="modal"
                  data-target="#confirm_modal"
                  data-id="{0}"
                  data-name="{1} {2}"
                  data-action="{3}">Delete</a> |
                  <a href="{4}">Edit</a>''',
                           record.id,
                           record.last_name,
                           record.first_name,
                           reverse('delete_user', args=[record.id]),
                           reverse('edit_user', args=[record.id]))

    class Meta:
        model = User
        # sequence = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'action')
        sequence = ('id', 'username', 'first_name', 'last_name', 'email', 'action')
        # fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'action')
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'action')
        attrs = {'class': 'table table-striped'}


class AdminDeviceTable(tables.Table):
    id = columns.Column(verbose_name='#')
    read_pipe = columns.Column(verbose_name='Read Pipe Key', empty_values=())
    write_pipe = columns.Column(verbose_name='Write Pipe Key', empty_values=())
    action = columns.Column(verbose_name='Action', empty_values=(), orderable=False)

    @staticmethod
    def render_action(record):
        return format_html('''<a href="#" class="delete_tag"
                  data-toggle="modal"
                  data-target="#confirm_modal"
                  data-id="{0}"
                  data-action="{1}">Delete</a> |
                  <a href="{2}">Edit</a>''',
                           record.id,
                           reverse('delete_device', args=[record.id]),
                           reverse('edit_device', args=[record.id]))
        # return format_html(
        #     render_to_string('basic_app/html/cells/admin_device_action.html',
        #                      {
        #                          'id': record.id,
        #                          'action': reverse('delete_device', args=[record.id]),
        #                          'edit_device': reverse('edit_device', args=[record.id]),
        #                      }))

    class Meta:
        model = Device
        sequence = ('id', 'read_pipe', 'write_pipe', 'action')
        fields = ('id', 'read_pipe', 'write_pipe', 'action')
        attrs = {'class': 'table table-striped'}



class MachineUsageTable(tables.Table):
    user = columns.Column(verbose_name="User", empty_values=())
    device = columns.Column(verbose_name="Device", empty_values=())
    time_on = columns.Column(verbose_name="Time On", empty_values=(), orderable=False)
    time_off = columns.Column(verbose_name="Time Off", empty_values=(), orderable=False)
    total_time = columns.Column(verbose_name="Total Time", empty_values=(), orderable=False)
    action = columns.Column(verbose_name='Action', empty_values=(), orderable=False)

    @staticmethod
    def render_action(record):
        return format_html('''<a href="#" class="delete_tag"
                  data-toggle="modal"
                  data-target="#confirm_modal"
                  data-id="{0}"
                  data-name="Device {1}"
                  data-action="{2}">Delete</a> |
                  <a href="{3}">Edit</a>''',
                           record.id,
                           record.device_id,
                           reverse('delete_machine_usage_entry', args=[record.id]),
                           reverse('edit_machine_usage_entry', args=[record.id]))

    class Meta:
        model = MachineUsage
        sequence = ('user', 'device', 'time_on', 'time_off', 'total_time', 'action')
        fields =  ('user', 'device', 'time_on', 'time_off', 'total_time', 'action')
        attrs = {'class': 'table table-striped'}

class GoogleSheetsTable(tables.Table):
    user = columns.Column(verbose_name="User", empty_values=())
    filename = columns.Column(verbose_name="Google Sheet Name", empty_values=())
    credentials = columns.Column(verbose_name="Credentials", empty_values=(), orderable=False)
    action = columns.Column(verbose_name='Action', empty_values=(), orderable=False)

    @staticmethod
    def render_action(record):
        return format_html('''{0}''',record.user.username)

    @staticmethod
    def render_action(record):
        return format_html('''<a href="#" class="delete_tag"
                  data-toggle="modal"
                  data-target="#confirm_modal"
                  data-id="{0}"
                  data-name="G Sheet: {1}"
                  data-action="{2}">Delete</a> |
                  <a href="{3}">Edit</a> | <a href="{4}">Sync</a>''',
                           record.id,
                           record.filename,
                           reverse('delete_google_sheet_entry', args=[record.id]),
                           reverse('edit_google_sheet_entry', args=[record.id]),
                           reverse('sync_google_sheet_entry', args=[record.id]))

    class Meta:
        model = GoogleSheet
        sequence = ('user', 'filename', 'credentials', 'action')
        fields =  ('user', 'filename', 'credentials', 'action')
        attrs = {'class': 'table table-striped'}