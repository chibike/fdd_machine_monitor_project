from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from basic_app.views import IndexView, ChangePasswordView, AdminView, NewUserView, LogoutView, DeleteUserView, EditUserView,\
    dummy_function, NewDeviceView, DeleteDeviceView, EditDeviceView, NewMachineUsageView, EditMachineUsageView,\
    DeleteMachineUsageView, DownloadMachineUsageView, ResetUsageDatabase, error_404, error_403, error_500, \
    NewGoogleSheetView, EditGoogleSheetView, DeleteGoogleSheetView, ResetGoogleSheetDatabase, SyncGoogleSheetView, \
    SyncAllGoogleSheet, get_device_usage_metrics, get_user_usage_metrics

from django.conf.urls import handler404, handler500, handler403
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boards/<str:card>', AdminView.as_view(), name='boards'),
    path('boards/', AdminView.as_view(), name='boards'),
    #path('dummy_function', dummy_function, name='dummy_function'),
    path('new_user/', NewUserView.as_view(), name='new_user'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete_user/<int:id>', DeleteUserView.as_view(), name='delete_user'),
    path('edit_user/<int:id>', EditUserView.as_view(), name='edit_user'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('new_device/', NewDeviceView.as_view(), name='new_device'),
    path('new_machine_usage_entry/', NewMachineUsageView.as_view(), name='new_machine_usage_entry'),
    path('edit_device/<str:id>', EditDeviceView.as_view(), name='edit_device'),
    path('edit_machine_usage_entry/<str:id>', EditMachineUsageView.as_view(), name='edit_machine_usage_entry'),
    path('download_machine_usage/', DownloadMachineUsageView.as_view(), name='download_machine_usage'),
    path('reset_usage_database/', ResetUsageDatabase.as_view(), name='reset_usage_database'),
    path('reset_google_sheet_database/', ResetGoogleSheetDatabase.as_view(), name='reset_google_sheet_database'),
    path('delete_device/<str:id>', DeleteDeviceView.as_view(), name='delete_device'),
    path('delete_machine_usage_entry/<str:id>', DeleteMachineUsageView.as_view(), name='delete_machine_usage_entry'),
    path('new_google_sheet_entry/', NewGoogleSheetView.as_view(), name='new_google_sheet_entry'),
    path('sync_all_google_sheets/', SyncAllGoogleSheet.as_view(), name='sync_all_google_sheets'),
    path('edit_google_sheet_entry/<str:id>', EditGoogleSheetView.as_view(), name='edit_google_sheet_entry'),
    path('sync_google_sheet_entry/<str:id>', SyncGoogleSheetView.as_view(), name='sync_google_sheet_entry'),
    path('delete_google_sheet_entry/<str:id>', DeleteGoogleSheetView.as_view(), name='delete_google_sheet_entry'),
    
    path('get_device_usage_metrics/', get_device_usage_metrics, name='get_device_usage_metrics'),
    path('get_user_usage_metrics/', get_user_usage_metrics, name='get_user_usage_metrics'),
    
    path('', IndexView.as_view(), name='index'),

    # path('accounts/', include('django.contrib.auth.urls')),
]

handler404 = 'basic_app.views.error_404'
handler403 = 'basic_app.views.error_403'
handler500 = 'basic_app.views.error_500'
