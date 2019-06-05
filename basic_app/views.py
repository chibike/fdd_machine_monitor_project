from django.http import Http404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_tables2 import RequestConfig

from basic_app.forms import LoginForm, ChangePasswordForm, UserFilterFormHelper, NewUserForm
from basic_app.tables import UserTable
from basic_app import support_functions
from basic_app import filters

class IndexView(AccessMixin, View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))
        login_form = LoginForm
        return render(request, 'basic_app/html/login.html', {'login_form': login_form, 'active_nav': 'index'})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.login()
            if user is not None:
                login(request, user)
                redirect_uri = request.GET.get(self.get_redirect_field_name(), None)
                if redirect_uri:
                    return redirect(redirect_uri)
                if user.is_superuser:
                    return redirect(reverse('admin'))
                else:
                    return redirect(reverse('dashboard'))
        return render(request, "basic_app/html/login.html", {'login_form': login_form, 'active_nav': 'index'})


class ChangePasswordView(LoginRequiredMixin, View):
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
        return redirect(reverse('dashboard'))

class AdminView(support_functions.TestIsSuperuser, View):
    @staticmethod
    def get(request, card='users'):
        card_list = ['users']
        card = card if card in card_list else 'users'

        parameters = {
                        'active_nav': 'admin',
                        'active_card': card
                    }

        if card == 'users':
            user_list = User.objects.all()
            user_filter = filters.UserFilter(request.GET, queryset=user_list)
            user_filter.form.helper = UserFilterFormHelper()
            table = UserTable(user_filter.qs)
            template = 'basic_app/html/admin_users.html'
            parameters['filter'] = user_filter
        

        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        parameters['table'] = table
        return render(request, template, parameters)

class AuthView(View):
    @staticmethod
    def post(request):
        logout(request)
        return redirect(reverse('index'))

class NewUserView(support_functions.TestIsSuperuser, View):
    @staticmethod
    def get(request):
        new_user_form = NewUserForm
        return render(request, 'basic_app/html/new_user.html', {'new_user_form': new_user_form})

    @staticmethod
    def post(request):
        new_user_form = NewUserForm(request.POST)
        if new_user_form.is_valid():
            new_user_form.save()
        else:
            return render(request, 'basic_app/html/new_user.html', {'new_user_form': new_user_form})
        return redirect(reverse('admin'))

class DeleteUserView(support_functions.TestIsSuperuser, View):
    @staticmethod
    def post(request, id):
        User.objects.get(pk=id).delete()
        return redirect(reverse('admin'))

class EditUserView(support_functions.TestIsSuperuser, View):
    @staticmethod
    def get(request, id):
        user = User.objects.get(pk=id)
        edit_user_form = NewUserForm(instance=user)
        return render(request, 'basic_app/html/new_user.html', {'new_user_form': edit_user_form})

    @staticmethod
    def post(request, id):
        user = User.objects.get(pk=id)
        edit_user_form = NewUserForm(request.POST, instance=user)
        if edit_user_form.is_valid():
            edit_user_form.save()
        else:
            return render(request, 'basic_app/html/new_user.html', {'new_user_form': edit_user_form})
        return redirect(reverse('admin'))

# class DashboardView(LoginRequiredMixin, View):
#     @staticmethod
#     def get(request, highlight=None):
#         user = request.user
#         ownership_list = user.ownership_set.all()
#         table = OwnershipTable(ownership_list)
#         has_certificate = True # has_certificate = hasattr(user, 'authorisationcertificate')
#         RequestConfig(request, paginate={'per_page': 10}).configure(table)
#         return render(request, 'basic_app/html/dashboard.html', {'table': table, 'has_certificate': has_certificate})


# class UpdateDashboard(LoginRequiredMixin, View):
#     @staticmethod
#     def get(request):
#         user = request.user
#         device_ids = [ownership.device.id for ownership in user.ownership_set.all()]
#         return JsonResponse(support_functions.get_js_for_device_status(device_ids))

def dummy_function(request):
    raise Http404("Oops! This page has not been implemented")
    return HttpResponse("Oops! This page has not been implemented")