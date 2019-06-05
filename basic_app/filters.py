import django_filters as filters
from django.contrib.auth.models import User
from django.db.models import Q

from basic_app.models import Device

class UserFilter(filters.FilterSet):
    SUPERUSER_CHOICES = {
        (True, 'Superusers'),
        (False, 'Normal users')
    }
    name = filters.CharFilter(method='any_name_filter')
    is_superuser = filters.ChoiceFilter(field_name='is_superuser', lookup_expr='exact',
                                        choices=SUPERUSER_CHOICES, empty_label='All')

    def any_name_filter(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(username__icontains=value)
        )

    class Meta:
        model = User
        fields = ['name', 'is_superuser']

class DeviceFilter(filters.FilterSet):
    id = filters.CharFilter(lookup_expr='icontains')
    read_pipe  = filters.CharFilter(lookup_expr='icontains')
    write_pipe = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Device
        fields = ['id', 'read_pipe', 'write_pipe']