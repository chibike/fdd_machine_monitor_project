from django.contrib import admin
from django.urls import path
from django.conf import settings

from basic_app.views import IndexView, ChangePasswordView, AdminView, NewUserView, AuthView, DeleteUserView, EditUserView,\
    dummy_function, NewDeviceView, DeleteDeviceView, DashboardView, EditDeviceView, NewMachineUsageView, EditMachineUsageView,\
    DeleteMachineUsageView, DownloadMachineUsageView, error_404, error_403, error_500

from django.conf.urls import handler404, handler500, handler403
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/<str:card>', AdminView.as_view(), name='admin'),
    path('admin/', AdminView.as_view(), name='admin'),
    path('dummy_function', dummy_function, name='dummy_function'),
    path('new_user/', NewUserView.as_view(), name='new_user'),
    path('logout/', AuthView.as_view(), name='logout'),
    path('delete_user/<int:id>', DeleteUserView.as_view(), name='delete_user'),
    path('edit_user/<int:id>', EditUserView.as_view(), name='edit_user'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('new_device/', NewDeviceView.as_view(), name='new_device'),
    path('new_machine_usage_entry/', NewMachineUsageView.as_view(), name='new_machine_usage_entry'),
    path('edit_device/<str:id>', EditDeviceView.as_view(), name='edit_device'),
    path('edit_machine_usage_entry/<str:id>', EditMachineUsageView.as_view(), name='edit_machine_usage_entry'),
    path('download_machine_usage/', DownloadMachineUsageView.as_view(), name='download_machine_usage'),
    path('delete_device/<str:id>', DeleteDeviceView.as_view(), name='delete_device'),
    path('delete_machine_usage_entry/<str:id>', DeleteMachineUsageView.as_view(), name='delete_machine_usage_entry'),
    path('dashboard/<str:highlight>', DashboardView.as_view(), name='dashboard'),
    path('', IndexView.as_view(), name='index'),
]

handler404 = 'basic_app.views.error_404'
handler403 = 'basic_app.views.error_403'
handler500 = 'basic_app.views.error_500'