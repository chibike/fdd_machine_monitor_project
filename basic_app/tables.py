from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import tables
from django_tables2.tables import columns

from basic_app.models import Device
import random

class UserTable(tables.Table):
    action = columns.Column(orderable=False, verbose_name='Action', empty_values=())
    id = columns.Column(verbose_name='#')
    is_superuser = columns.Column(verbose_name='Superuser')

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
        sequence = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'action')
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'action')
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
        attrs = {'class': 'table table-striped'}