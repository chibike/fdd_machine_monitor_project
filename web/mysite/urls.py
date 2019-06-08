from django.contrib import admin
from django.urls import path

from basic_app.views import IndexView, ChangePasswordView, AdminView, NewUserView, AuthView, DeleteUserView, EditUserView, dummy_function, NewDeviceView, DeleteDeviceView, DashboardView, EditDeviceView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/<str:card>', AdminView.as_view(), name='admin'),
    path('admin/', AdminView.as_view(), name='admin'),
    path('dummy_function', dummy_function, name='dummy_function'),
    path('new_user/', NewUserView.as_view(), name='new_user'),
    path('dashboard/', dummy_function, name='dashboard'),
    path('logout/', AuthView.as_view(), name='logout'),
    path('delete_user/<int:id>', DeleteUserView.as_view(), name='delete_user'),
    path('edit_user/<int:id>', EditUserView.as_view(), name='edit_user'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('new_device', NewDeviceView.as_view(), name='new_device'),
    path('edit_device/<str:id>', EditDeviceView.as_view(), name='edit_device'),
    path('delete_device/<str:id>', DeleteDeviceView.as_view(), name='delete_device'),
    path('dashboard/<str:highlight>', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', IndexView.as_view(), name='index')
]
