from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

is_superuser = lambda u : u.is_superuser
is_authenticated = lambda u : u.is_authenticated

class TestIsSuperuser(UserPassesTestMixin):
    def test_func(self):
        return is_superuser(self.request.user)

    raise_exception = True


def get_logged_users() -> list:
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    return User.objects.filter(id__in=uid_list)