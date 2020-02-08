from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django_tables2 import RequestConfig
from django.urls import reverse
from django.views import View

from basic_app.forms import LoginForm, ChangePasswordForm, UserFilterFormHelper, NewUserForm
from basic_app.forms import NewDeviceForm, DeviceFilterFormHelper, MachineUsageFilterFormHelper
from basic_app.forms import NewMachineEntryForm, NewGoogleSheetEntryForm, GoogleSheetEntryFormHelper
from basic_app.tables import UserTable, AdminDeviceTable, MachineUsageTable, GoogleSheetsTable
from basic_app.models import Device, MachineUsage, GoogleSheet, UserWrapper
from basic_app import support_functions
from basic_app import filters
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator

from device_manager import device_manager
import pandas as pd
import json

device_node_manager = device_manager.DeviceManager()
device_node_manager.initialize()
device_node_manager.print_details()

def device_statechange_callback_handler(device):
    print ("'{name}' is '{state}'".format(name=device.name, state=device.get_state()))
    
    try:
        _device = Device.objects.get(id=device.id)
        _device.state = device.get_state()
        _device.save()

        # device was switched off
        if not device.get_state():
            timestamp = device.get_timestamp()

            try:
                _user = User.objects.filter(id__exact=device.get_user())[-1][0]
            except:
                _user = User.objects.all()[0]

            _usage = MachineUsage(user=_user, device=_device, time_on=timestamp["time_on"], time_off=timestamp["time_off"], total_time=timestamp["total_time"])
            _usage.save()
    except Exception as e:
        print ("Exception while handling device state change")
        print ("device: {}".format(device))
        print ("Exception: {}".format(e))

def load_devices():
    print ("loading your devices")
    device_node_manager.clear_devices()
    devices = Device.objects.all()

    for device in devices:
        _device = device_manager.Device(str(device), device.id)
        _device.initialize(pipe_a=eval(device.read_pipe), pipe_b=eval(device.write_pipe))
        _device.add_state_change_callback("tag", device_statechange_callback_handler)
        device_node_manager.add_device(hash(device), _device)

load_devices()
device_node_manager.run()


def get_device_usage_metrics(request, exception=None):
    return HttpResponse(json.dumps(Device.get_devices_usage_metrics()))


def get_user_usage_metrics(request, exception=None):
    return HttpResponse(json.dumps(UserWrapper.get_users_usage_metrics()))


class IndexView(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect(reverse('boards'))
        login_form = LoginForm
        return render(request, 'basic_app/html/login.html', {'login_form': login_form, 'active_nav': 'index'})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.login()
            if user is not None:
                login(request, user)
                # redirect_uri = request.GET.get(self.get_redirect_field_name(), None)
                # if redirect_uri:
                #     return redirect(redirect_uri)
                
                return redirect(reverse('boards'))
        return render(request, "basic_app/html/login.html", {'login_form': login_form, 'active_nav': 'index'})


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        change_password_form = ChangePasswordForm
        return render(request, 'basic_app/html/change_password.html', {'change_password_form': change_password_form,
                                                             'active_nav': 'change_password'})

    @staticmethod
    def post(request):
        user = request.user
        change_password_form = ChangePasswordForm(user, request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
        else:
            return render(request, 'basic_app/html/change_password.html', {'change_password_form': change_password_form,
                                                                 'active_nav': 'change_password'})
        return redirect(reverse('boards'))

class AdminView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, card='users'):
        card_list = ['users', 'devices', 'machine_usage', 'google_sheet', 'graphs']
        card = card if card in card_list else 'users'

        parameters = {
                        'active_nav': 'boards',
                        'active_card': card
                    }

        if card == 'users':
            user_list = User.objects.all()
            user_filter = filters.UserFilter(request.GET, queryset=user_list)
            user_filter.form.helper = UserFilterFormHelper()
            template = 'basic_app/html/admin_users.html'
            parameters['table'] = UserTable(user_filter.qs)
            parameters['filter'] = user_filter
        elif card == 'devices':
            device_list = Device.objects.all()
            device_filter = filters.DeviceFilter(request.GET, queryset=device_list)
            device_filter.form.helper = DeviceFilterFormHelper()
            template = 'basic_app/html/admin_devices.html'
            parameters['table'] = AdminDeviceTable(device_filter.qs)
            parameters['filter'] = device_filter
        elif card == 'machine_usage':
            usage_list = MachineUsage.objects.all()
            usage_filter = filters.MachineUsageFilter(request.GET, queryset=usage_list)
            usage_filter.form.helper =  MachineUsageFilterFormHelper()
            template = 'basic_app/html/admin_machine_usage.html'
            parameters['table'] = MachineUsageTable(usage_filter.qs)
            parameters['filter'] = usage_filter
        elif card == 'google_sheet':
            sheet_list = GoogleSheet.objects.all()
            sheet_filter = filters.GoogleSheetFilter(request.GET, queryset=sheet_list)
            sheet_filter.form.helper =  GoogleSheetEntryFormHelper()
            template = 'basic_app/html/admin_google_sheet.html'
            parameters['table'] = GoogleSheetsTable(sheet_filter.qs)
            parameters['filter'] = sheet_filter
        elif card == 'graphs':
            template = 'basic_app/html/admin_graphs.html'
        if 'table' in parameters.keys():
            RequestConfig(request, paginate={'per_page': 30}).configure(parameters['table'])

        return render(request, template, parameters)

class NewDeviceView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        new_device_form = NewDeviceForm
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_device_form})

    @staticmethod
    def post(request):
        new_device_form = NewDeviceForm(request.POST)
        if new_device_form.is_valid():
            new_device_form.save()
            load_devices()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_device_form})
        return redirect(reverse('boards', args=['devices']))

class DeleteDeviceView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, id):
        Device.objects.get(id=id).delete()
        load_devices()
        return redirect(reverse('boards', args=['devices']))

class EditDeviceView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, id):
        device = Device.objects.get(pk=id)
        edit_device_form = NewDeviceForm(instance=device)
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_device_form})

    @staticmethod
    def post(request, id):
        device = Device.objects.get(pk=id)
        edit_device_form = NewDeviceForm(request.POST, instance=device)
        if edit_device_form.is_valid():
            edit_device_form.save()
            load_devices()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_device_form})
        return redirect(reverse('boards'))

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    @staticmethod
    def post(request):
        logout(request)
        return redirect(reverse('index'))

@method_decorator(csrf_exempt, name='dispatch')
class DownloadMachineUsageView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        filename = "machine_usage.csv"
        df = pd.DataFrame(list(MachineUsage.objects.all().values()))
        df.to_csv(filename)
        
        response = FileResponse(open(filename, 'rb'), content_type="application/csv")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response

@method_decorator(csrf_exempt, name='dispatch')
class ResetUsageDatabase(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        MachineUsage.objects.all().delete()
        return redirect('/boards/machine_usage')

class NewUserView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        new_user_form = NewUserForm
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_user_form})

    @staticmethod
    def post(request):
        new_user_form = NewUserForm(request.POST)
        if new_user_form.is_valid():
            new_user_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_user_form})
        return redirect('/boards/users')

class DeleteUserView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def post(request, id):
        User.objects.get(pk=id).delete()
        return redirect('/boards/users')

class EditUserView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, id):
        user = User.objects.get(pk=id)
        edit_user_form = NewUserForm(instance=user)
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_user_form})

    @staticmethod
    def post(request, id):
        user = User.objects.get(pk=id)
        edit_user_form = NewUserForm(request.POST, instance=user)
        if edit_user_form.is_valid():
            edit_user_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_user_form})
        return redirect('/boards/users')

class NewMachineUsageView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        new_machine_usage_entry_form = NewMachineEntryForm
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_machine_usage_entry_form})

    @staticmethod
    def post(request):
        new_machine_usage_entry_form = NewMachineEntryForm(request.POST)
        if new_machine_usage_entry_form.is_valid():
            new_machine_usage_entry_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_machine_usage_entry_form})
        return redirect('/boards/machine_usage')


class EditMachineUsageView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, id):
        machine_usage_entry = MachineUsage.objects.get(pk=id)
        edit_machine_usage_entry_form = NewMachineEntryForm(instance=machine_usage_entry)
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_machine_usage_entry_form})

    @staticmethod
    def post(request, id):
        machine_usage_entry = MachineUsage.objects.get(pk=id)
        edit_machine_usage_entry_form = NewMachineEntryForm(request.POST, instance=machine_usage_entry)
        if edit_machine_usage_entry_form.is_valid():
            edit_machine_usage_entry_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_machine_usage_entry_form})
        return redirect('/boards/machine_usage')

class DeleteMachineUsageView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def post(request, id):
        MachineUsage.objects.get(pk=id).delete()
        return redirect('/boards/machine_usage')

class NewGoogleSheetView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        new_google_sheet_entry_form = NewGoogleSheetEntryForm
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_google_sheet_entry_form})

    @staticmethod
    def post(request):
        new_google_sheet_entry_form = NewGoogleSheetEntryForm(request.POST, request.FILES)
        if new_google_sheet_entry_form.is_valid():
            new_google_sheet_entry_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': new_google_sheet_entry_form})
        return redirect('/boards/google_sheet')

class EditGoogleSheetView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, id):
        google_sheet_entry = GoogleSheet.objects.get(pk=id)
        edit_google_sheet_entry_form = NewGoogleSheetEntryForm(instance=google_sheet_entry)
        return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_google_sheet_entry_form})

    @staticmethod
    def post(request, id):
        google_sheet_entry = GoogleSheet.objects.get(pk=id)
        edit_google_sheet_entry_form = NewGoogleSheetEntryForm(request.POST, request.FILES, instance=google_sheet_entry)
        if edit_google_sheet_entry_form.is_valid():
            edit_google_sheet_entry_form.save()
        else:
            return render(request, 'basic_app/html/create_new_form.html', {'create_new_form': edit_google_sheet_entry_form})
        return redirect('/boards/google_sheet')

class SyncGoogleSheetView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request, id):
        GoogleSheet.objects.get(pk=id).sync()
        return redirect('/boards/google_sheet')

class DeleteGoogleSheetView(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def post(request, id):
        GoogleSheet.objects.get(pk=id).delete()
        return redirect('/boards/google_sheet')

@method_decorator(csrf_exempt, name='dispatch')
class ResetGoogleSheetDatabase(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        [obj.delete() for obj in GoogleSheet.objects.all()]
        return redirect('/boards/google_sheet')

@method_decorator(csrf_exempt, name='dispatch')
class SyncAllGoogleSheet(LoginRequiredMixin, View):
    login_url = '/'

    @staticmethod
    def get(request):
        GoogleSheet.sync_all()
        return redirect('/boards/google_sheet')

def error_403(request, exception=None):
    data = {}
    return render(request, '403.html', data)

def error_404(request, exception=None):
    data = {}
    return render(request, '404.html', data)

def error_500(request, exception=None):
    data = {}
    return render(request, '500.html', data)


def dummy_function(request):
    raise Http404("Oops! This page has not been implemented")
