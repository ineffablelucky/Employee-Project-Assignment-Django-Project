from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import Group
from .models import Company, Employee, Project, Module, MyUser


class AddEditCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

    def clean_company_name(self):
        """
        :return: company_name if it does not already exists in the database
        else raises validation error
        """
        data = self.cleaned_data.get('company_name').title()

        try:

            obj = Company.objects.get(company_name=data)
            if data == obj.company_name:
                return data
            raise forms.ValidationError('Company already exists. Choose a unique name')

        except Company.DoesNotExist:
            return data

    def clean_year(self):
        """
        :return:  year if it exists in the mentioned range else returns validation error
        """
        data = self.cleaned_data.get('year')

        if 2100 > data > 1800:
            return data
        raise forms.ValidationError("Year Range 1801-2099")


class EditEmployeeForm(forms.ModelForm):
    date_of_joining = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,  # DATE_INPUT_FORMATS = ['%d-%m-%Y']
                                      help_text='It must be in DD-MM-YYYY format.',
                                      widget=forms.widgets.DateInput(format="%d-%m-%Y"))  # to get data from database
    # and render in html form in a particular format

    class Meta:
        model = Employee
        fields = '__all__'  # date_of_joining Model-field from models.py is overridden by date_of_joining FormField

    def clean_age(self):
        """
        :return: checks if the age entered is in range
        """
        data = self.cleaned_data.get('age')

        if 17 < data < 66:
            return data
        raise forms.ValidationError("Incorrect age. Check the range")


class AddEditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def clean_project_name(self):
        """
        https://stackoverflow.com/questions/20564856/django-exclude-self-from-queryset-for-validation
        :return: checks existing project name in the same company
        """
        data = self.cleaned_data['project_name'].title()
        comp = self.cleaned_data.get('company')
        qs = Project.objects.filter(Q(company=comp) & Q(project_name=data))
        if self.instance.pk is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("There is already a project with name: %s" % data)
        return data

    def clean_team_leader(self):
        """
        :return: checks if team leader is one of the team members on the project
        """
        data = self.cleaned_data.get('team_leader')
        selected_member = self.cleaned_data.get('team_members').__dict__['_result_cache']

        if data not in selected_member:
            raise forms.ValidationError("The team leader must be one of the selected team members")
        return data


class AddEditModuleForm(forms.ModelForm):
    start_date = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,  # ['%d-%m-%Y %H:%M:%S']
                                     initial=datetime.now(),
                                     help_text='It must be in DD-MM-YYYY HH:MM 24-hour format.',
                                     widget=forms.widgets.DateTimeInput(
                                         format="%d-%m-%Y %H:%M"))

    end_date = forms.DateTimeField(input_formats=settings.DATETIME_INPUT_FORMATS,  # ['%d-%m-%Y %H:%M:%S']
                                   initial=datetime.now(),
                                   help_text='It must be in DD-MM-YYYY HH:MM 24-hour format.',
                                   widget=forms.widgets.DateTimeInput(
                                       format="%d-%m-%Y %H:%M"))

    class Meta:
        model = Module
        fields = '__all__'

    def clean_module_name(self):
        data = self.cleaned_data.get('module_name').title()
        return data

    def clean_end_date(self):
        """
        to do date comparison
        :return: error is end date is earlier than start date
        """

        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')

        if end_date <= start_date:
            raise forms.ValidationError("End date and time should be later than start date")
        return end_date


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=200)
    full_name = forms.CharField(required=True, max_length=100)

    class Meta:
        model = MyUser
        fields = ('email', 'full_name', 'designation', 'password1', 'password2')
        exclude = ('username', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email'].lower().split('@')[0]

        if commit:
            # to read more about transactions in django : https://docs.djangoproject.com/en/2.0/topics/db/transactions/
            with transaction.atomic():

                user.save()  # user is saved first, to create its id so that Group can add user's id
                designation = self.cleaned_data['designation']

                if designation == 'Admin':
                    group_user = Group.objects.get_by_natural_key('Admin Group')
                    group_user.user_set.add(user)
                elif designation == 'Team Leader':
                    group_user = Group.objects.get_by_natural_key('Team Leader Group')
                    group_user.user_set.add(user)
                elif designation == 'Employee':
                    group_user = Group.objects.get_by_natural_key('Low Level Employee Group')
                    group_user.user_set.add(user)
                else:
                    raise Exception("Not correct designation")

        return user

    def clean_designation(self):
        data = self.cleaned_data.get('designation')
        choices = ['Employee', 'Team Leader', 'Admin']

        if data in choices:
            return data
        raise forms.ValidationError("Choose correct designation!!")

    def clean_email(self):
        data = self.cleaned_data.get('email').lower()

        try:
            MyUser.objects.get(email=data)
            raise forms.ValidationError('Email already exists. Choose a unique name')

        except MyUser.DoesNotExist:
            return data

    def clean_full_name(self):
        """
        :return:  if valid, full name in title form with white spaces are either end removed
        """
        data = self.cleaned_data.get('full_name').title()
        if data.replace(" ", "").isalpha():
            return data.strip()
        raise forms.ValidationError("Enter correct name using alphabets and single space")