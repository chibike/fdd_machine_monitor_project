from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field, ButtonHolder, Fieldset

from basic_app.models import Device, MachineUsage, GoogleSheet

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', max_length=50, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'login_form'
        self.helper.form_method = 'post'
        # self.helper.form_action = '/'

        self.helper.form_show_labels = False
        # self.helper.form_class = 'my-auto'

        self.helper.layout = Layout(
            Div(
                Field('username', css_class='form-control w-100', placeholder='Username'), css_class='form-group'
            ),
            Div(
                Field('password', css_class='form-control w-100', placeholder='Password'), css_class='form-group'
            ),
            Submit('submit', 'Log in!', css_class='btn btn-primary w-100')
        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            self.add_error('username', '')
            self.add_error('password', 'Username or password is incorrect.')
        return self.cleaned_data

    def login(self) -> User:
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class ChangePasswordForm(forms.Form):
    password = forms.CharField(label='Password', max_length=50,  widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm password', max_length=50, widget=forms.PasswordInput)

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                Field('password', css_class='form-control w-100', placeholder='New Password'), css_class='form-group'
            ),
            Div(
                Field('confirm_password', css_class='form-control w-100', placeholder='Confirm Password'), css_class='form-group'
            ),
            Submit('submit', 'Change', css_class='btn btn-primary w-100')
        )

        # self.helper.layout = Layout(
        #     Fieldset(
        #         'Change password',
        #         'password',
        #         'confirm_password',
        #         ButtonHolder(
        #             Submit('submit', 'Change')
        #         )
        #     )
        # )

        pass

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords are different.')
        else:
            try:
                validate_password(password)
            except ValidationError as ex:
                self.add_error('password', ex.messages)
        return self.cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

class UserFilterFormHelper(FormHelper):
    _form_method = 'GET'
    form_class = 'form-inline float-left'
    form_show_labels = False
    layout = Layout(
        Field('name', placeholder='Name', css_class='mr-2'),
        Field('is_superuser', css_class='mr-2'),
        ButtonHolder(
            Submit('submit', 'Apply filters')
        )
    )

class NewUserForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, max_length=50)
    confirm_password = forms.CharField(label='Confirm password', widget=forms.PasswordInput, max_length=50)

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(
                Field('username', css_class='form-control w-100', placeholder='Username'), css_class='form-group'
            ),
            Div(
                Field('first_name', css_class='form-control w-100', placeholder='First Name'), css_class='form-group'
            ),
            Div(
                Field('last_name', css_class='form-control w-100', placeholder='Last Name'), css_class='form-group'
            ),
            Div(
                Field('email', css_class='form-control w-100', placeholder='Email'), css_class='form-group'
            ),
            Div(
                Field('password', css_class='form-control w-100', placeholder='Password'), css_class='form-group'
            ),
            Div(
                Field('confirm_password', css_class='form-control w-100', placeholder='Confirm Password'), css_class='form-group'
            ),
            Div(
                Field('is_superuser')
            ),
            Submit('submit', 'Save', css_class='btn btn-primary w-100')
            
            )
        self.edit_mode = self.instance.id is not None

        if self.edit_mode:
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
            self.initial['password'] = ''
            self.fields['password'].help_text = 'Leave empty if you don\'t want to change password.'

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', 'Passwords are different.')
        else:
            try:
                if self.instance.id is None or len(password) > 0:
                    validate_password(password)
            except ValidationError as ex:
                self.add_error('password', ex.messages)

        if len(User.objects.filter(username=username)) > (0 if not self.edit_mode else 1):
            self.add_error('username', 'Username is taken.')
        if email and len(User.objects.filter(email=email)) > (0 if not self.edit_mode else 1):
            self.add_error('email', 'Account with this email exists.')

        return self.cleaned_data

    def save(self, commit=True):
        instance = super(NewUserForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            instance.set_password(self.cleaned_data.get('password'))
        else:
            old_password = User.objects.get(pk=instance.id).password
            instance.password = old_password
        if commit:
            instance.save()
        return instance

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_superuser', 'password']

class NewDeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewDeviceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
                Div(
                    Field('id', css_class='form-control w-100', placeholder='0'), css_class='form-group'
                ),
                Div(
                    Field('read_pipe', css_class='form-control w-100', placeholder='Read Pipe'), css_class='form-group'
                ),
                Div(
                    Field('write_pipe', css_class='form-control w-100', placeholder='Write Pipe'), css_class='form-group'
                ),
                Submit('submit', 'Save', css_class='btn btn-primary w-100')
            )

    def save(self, commit=True):
        instance = super(NewDeviceForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Device
        fields = ['id', 'read_pipe', 'write_pipe']

class DeviceFilterFormHelper(FormHelper):
    _form_method = 'GET'
    form_class = 'form-inline float-left'
    form_show_labels = False
    layout = Layout(
        Field('id', placeholder='Device ID', css_class='mr-2'),
        Field('read_pipe', placeholder='Read Pipe', css_class='mr-2'),
        Field('write_pipe', placeholder='Write Pipe', css_class='mr-2'),
        ButtonHolder(
            Submit('submit', 'Apply filters')
        )
    )

class NewMachineEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewMachineEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
                Div(
                    Field('user', css_class='form-control w-100'), css_class='form-group'
                ),
                Div(
                    Field('device', css_class='form-control w-100'), css_class='form-group'
                ),
                Div(
                    Field('time_on', css_class='form-control w-100'), css_class='form-group'
                ),
                Div(
                    Field('time_off', css_class='form-control w-100'), css_class='form-group'
                ),
                Div(
                    Field('total_time', css_class='form-control w-100'), css_class='form-group'
                ),
                Submit('submit', 'Save', css_class='btn btn-primary w-100')
            )

    def save(self, commit=True):
        instance = super(NewMachineEntryForm, self).save(commit=False)
        if commit:
            instance.save()
            instance.update_gsheet()
        return instance

    class Meta:
        model = MachineUsage
        fields = ['user', 'device', 'time_on', 'time_off', 'total_time']

class MachineUsageFilterFormHelper(FormHelper):
    _form_method = 'GET'
    form_class = 'form-inline float-left'
    form_show_labels = False

    layout = Layout(
        Field('user', placeholder="User", css_class='mr-2'),
        Field('device', placeholder="Device", css_class='mr-2'),
        ButtonHolder(
            Submit('submit', 'Apply filters')
        )
    )
# title = forms.CharField(max_length=50)
    # file = forms.FileField()
class NewGoogleSheetEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewGoogleSheetEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
                Div(
                    Field('user', css_class='form-control w-100'), css_class='form-group'
                ),
                Div(
                    Field('filename', css_class='form-control w-100'), css_class='form-group'
                ),
                Field('credentials', css_class='form-control w-100')
                ,
                Submit('submit', 'Save', css_class='btn btn-primary w-100')
            )

    def save(self, commit=True):
        instance = super(NewGoogleSheetEntryForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = GoogleSheet
        fields = ['user', 'filename', 'credentials']
        labels = {
            'filename': _('Google Sheet Name'),
        }

class GoogleSheetEntryFormHelper(FormHelper):
    _form_method = 'GET'
    form_class = 'form-inline float-left'
    form_show_labels = False

    layout = Layout(
        Field('user', placeholder="User", css_class='mr-2'),
        Field('filename', placeholder="Google Sheet Name", css_class='mr-2'),
        ButtonHolder(
            Submit('submit', 'Apply filters')
        )
    )
