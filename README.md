# django_project_template
Basic Django Template Complete with Admin and User Login

### Dependencies ###

This repo contains the following dependencies:

#### System Dependencies ####

1. Python3
2. Git
3. Virtualenv
4. Virtualenvwrapper

#### Python Dependencies ####

1. Django==2.1
2. django-crispy-forms==1.7.2
2. django-filter==2.0.0
3. django-tables2==2.0.0a5
4. django-yarn==0.0.1

### Installation ###

1. Install the Essentials - Python, Git, Vscode, Virtualenv etc

```
wget https://raw.githubusercontent.com/chibike/shell_scripts/master/ubuntu_essentials.sh

chmod +x ubuntu_essentials.sh

./ubuntu_essentials.sh

rm ubuntu_essentials.sh

```

2. Install Python Dependencies

```
sudo pip3 install -r requirements.txt
```

3. Setup your Git Account

Run

```
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
```

to set your account's default identity.
Omit --global to set the identity only in this repository.

4. First Time Setup

Run

```
python manage.py makemigrations basic_app
python manage.py sqlmigrate basic_app 0001
python manage.py createsuperuser
python manage.py migrate

```

For the created user:

```
Username: admin
Email address: your email address
Password: justapass
```

### Execution ###

To Start the Server

```
python manage.py runserver 0:8000
```

### Code Structure ###
