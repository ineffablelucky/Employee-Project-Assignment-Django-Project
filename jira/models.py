from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.conf import settings
from datetime import date


class MyUser(AbstractUser):  # add AUTH_USER_MODEL = 'jira.MyUser' in settings.py

    DESIGNATION_CHOICES = (
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
        ('Team Leader', 'Team Leader'),
    )

    # username will not unique for people having different domain name but same local-part of email id
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=False, unique=True, max_length=200)
    designation = models.CharField(blank=False, choices=DESIGNATION_CHOICES, max_length=200, default=None)
    full_name = models.CharField(blank=False, unique=False, max_length=100, default=None)

    REQUIRED_FIELDS = ['designation', 'full_name', 'username']
    USERNAME_FIELD = 'email'  # making user login using email, not username

    def __str__(self):
        return '%s' % self.full_name

    class Meta:
        permissions = (
            ('can_register', 'Can Register New People'),
        )

# https://hashedin.com/2017-05-30-configure-role-based-access-control-in-django/
# https://medium.com/@theparadoxer02/user-groups-with-custom-permissions-in-django-9eaea67b220e
# https: // www.vinta.com.br / blog / 2016 / controlling - access - a - django - permission - apps - comparison /
# https://docs.djangoproject.com/en/2.0/topics/auth/default/
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/
# https://django-registration.readthedocs.io/en/2.4.1/custom-user.html
# https://medium.com/@ramykhuffash/django-authentication-with-just-an-email-and-password-no-username-required-33e47976b517


class Employee(models.Model):
    # choices for gender model

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    employee = models.OneToOneField(MyUser, related_name="my_user", on_delete=models.CASCADE, default=None)
    age = models.PositiveIntegerField(null=False, help_text="Age between 18 and 65", default=0)
    date_of_joining = models.DateField(auto_created=True, default=date.today)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    salary = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '{}'.format(self.employee)

    class Meta:
        permissions = (
            ('view_employees', 'Can View Employees'),
        )


def create_profile(sender, **kwargs):
    if kwargs['created']:  # to create and fill employee model with respective user with post_save signal
        user_profile = Employee.objects.create(employee=kwargs['instance'])


post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)


class Company(models.Model):

    company_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False)  # Note: blank is by-default False
    """
    null is used for database entries
    blank is for form validation
    https://docs.djangoproject.com/en/2.0/ref/models/fields/
    """

    def __str__(self):
        return '%s' % self.company_name

    class Meta:
        permissions = (
            ('view_company', 'Can View Company'),
        )


class Project(models.Model):

    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    project_code = models.CharField(max_length=50, unique=True, default=None)
    project_name = models.CharField(max_length=200, unique=False, default=None)
    team_members = models.ManyToManyField(Employee, related_name='team_employees')
    team_leader = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='team_leader', default=None)

    def __str__(self):
        return '{} project of company {}'.format(self.project_name, self.company)

    class Meta:
        permissions = (
            ('view_projects', 'Can View Projects'),
        )


class Module(models.Model):

    module_name = models.CharField(max_length=200)
    module_code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.OneToOneField(Employee, related_name='employer_model', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    assignee = models.ForeignKey(Employee, related_name='assignee', on_delete=models.CASCADE)

    def __str__(self):
        return '{} module of {} for employee {} '.format(self.module_name, self.project, self.employee)

    class Meta:
        permissions = (
            ('view_modules', 'Can View Modules'),
        )
