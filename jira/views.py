from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.views import generic

# for login restrictions
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
# LOGIN_URL = 'login' in settings.py
# LOGIN_REDIRECT_URL = 'company_list_view'

from .models import Company, Employee, Project, Module, MyUser
from .forms import (AddEditCompanyForm, EditEmployeeForm, AddEditProjectForm, AddEditModuleForm,
                    UserRegistrationForm)


# LOGIN_URL = 'login'
# LOGIN_REDIRECT_URL = 'company_list_view'
@login_required
@permission_required('jira.can_register', raise_exception=True)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid:
            try:
                form.save()
                messages.success(request, "{} registered".format(form.cleaned_data['email']))
                return redirect('company_list_view')

            except ValueError:
                return render(request, 'register_form.html', {'form': form})

            except Exception:
                messages.warning(request, "Exception error")
                return render(request, 'register_form.html', {'form': form})
    else:
        form = UserRegistrationForm()

    return render(request, 'register_form.html', {'form': form})


@login_required
def company_view(request):
    """
    :param request: GET request
    :return: all companies' details are passed to HTML template if user belongs to Admin Group
    """

    if request.user.groups.filter(name='Admin Group').exists():
        return render(request, 'company_list.html', {'companies': Company.objects.all()})

    raise PermissionDenied


@login_required
def add_company(request):
    """
    :param request: GET, POST
    :return: form saved if successful and redirected to company table view
    """
    if not request.user.groups.filter(name='Admin Group').exists():
        raise PermissionDenied

    if request.method == 'POST':
        form = AddEditCompanyForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "{} added".format(form.cleaned_data['company_name'].title()))

            if request.GET.get('redirect_next'):
                return redirect('employee_list_view')
            return redirect('company_list_view')

    else:
        form = AddEditCompanyForm()
    return render(request, 'add_company.html', {'form': form})


@login_required
def update_company(request, company_id):
    """
    :param company_id: respective company id arrives with request
    :return: saves the updated details of the company
    """
    if not request.user.groups.filter(name='Admin Group').exists():
        raise PermissionDenied

    if request.method == 'POST':
        form = AddEditCompanyForm(request.POST, instance=Company.objects.get(id=company_id))

        if form.is_valid():
            form.save()
            messages.success(request, "{} added".format(form.cleaned_data['company_name'].title()))
            return redirect('company_list_view')

    else:
        form = AddEditCompanyForm(instance=get_object_or_404(Company, id=company_id))

    return render(request, 'update_company.html', {'form': form})


@login_required
def delete_company(request, company_id):
    """
    :param company_id: id of the company which user wants to delete.
    :return: deletes the company from database and returns a message
    """
    if not request.user.groups.filter(name='Admin Group').exists():
        raise PermissionDenied

    try:
        company_name = Company.objects.get(id=company_id)
        company_name.delete()
        messages.warning(request, 'Deleted company: {}'.format(company_name))

    except Exception as e:
        messages.warning(request, 'Got an error when trying to delete a company: {}.'.format(e))

    return redirect('company_list_view')


class EmployeeView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
        Generic View to View all Employees
    """
    permission_required = 'jira.view_employees'
    raise_exception = True
    template_name = 'employee_list_view.html'
    context_object_name = 'employees'
    model = Employee


"""
EmployeeCreateView removed as Employee will be created with register page
"""

# class EmployeeCreateView(LoginRequiredMixin, generic.CreateView):
#     """
#         Generic View to Create an Employee
#     """
#     template_name = 'add_employee.html'
#     model = Employee
#     form_class = AddEditEmployeeForm
#     success_url = reverse_lazy('employee_list_view')
#
#     def form_valid(self, form):
#         result = super().form_valid(form)
#         messages.success(
#             self.request, '{} created'.format(form.instance))
#         return result


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    """
        Generic View to Update an Employee
    """
    permission_required = 'jira.change_employee'
    raise_exception = True
    form_class = EditEmployeeForm
    template_name = 'update_employee.html'
    model = Employee
    success_url = reverse_lazy('employee_list_view')

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} updated'.format(form.instance))
        return result


class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    """
    Generic View to Delete an Employee
    """
    permission_required = 'jira.delete_employee'
    raise_exception = True
    template_name = 'delete_employee.html'
    model = Employee
    success_url = reverse_lazy('module_list_view')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """

        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.employee.delete()  # deleting the object of MyUser model that will lead to deletion of
        # object in employee model , self.object.delete()

        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        if self.success_url:
            messages.warning(
                self.request, '{} deleted'.format(self.object.employee.email))
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")


class ProjectView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
        Generic View to View all projects
    """
    permission_required = 'jira.view_projects'
    raise_exception = True
    template_name = 'project_list_view.html'
    context_object_name = 'projects'
    model = Project

    def get_queryset(self):

        if self.request.user.groups.filter(name='Admin Group').exists():
            return Project.objects.all()

        elif self.request.user.groups.filter(name='Team Leader Group').exists():
            employee_id = MyUser.objects.get(id=self.request.user.id)
            return employee_id.team_leader.all()

        elif self.request.user.groups.filter(name='Low Level Employee Group').exists():
            employee_id = MyUser.objects.get(id=self.request.user.id)
            return employee_id.team_employees.all()

        raise PermissionDenied


class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    """
        Generic View to Create an project
    """
    permission_required = 'jira.add_project'
    raise_exception = True
    template_name = 'add_project.html'
    model = Project
    form_class = AddEditProjectForm
    success_url = reverse_lazy('project_list_view')

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} created'.format(form.instance))
        return result


class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    """
        Generic View to Update an project
    """
    permission_required = 'jira.change_project'
    raise_exception = True
    form_class = AddEditProjectForm
    template_name = 'update_project.html'
    model = Project
    success_url = reverse_lazy('project_list_view')

    def get(self, request, *args, **kwargs):

        if self.request.user.groups.filter(name='Team Leader Group').exists():
            self.object = self.get_object()
            employee_id = MyUser.objects.get(id=self.request.user.id)
            if self.object in employee_id.team_leader.all():
                return super().get(request, *args, **kwargs)
            raise PermissionDenied

        elif self.request.user.groups.filter(name='Admin Group').exists():
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)

        raise PermissionDenied

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} updated'.format(form.instance))
        return result


class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    """
    Generic View to Delete an project
    """
    permission_required = 'jira.delete_project'
    raise_exception = True
    template_name = 'delete_project.html'
    model = Project
    success_url = reverse_lazy('project_list_view')

    def get_success_url(self):
        if self.success_url:
            messages.warning(
                self.request, '{} deleted'.format(self.object.__dict__['project_name']))
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")


class ModuleView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """
        Generic View to View all Modules
    """
    permission_required = 'jira.view_modules'
    raise_exception = True
    template_name = 'module_list_view.html'
    context_object_name = 'modules'
    model = Module

    def get_queryset(self):

        if self.request.user.groups.filter(name='Admin Group').exists():
            return Module.objects.all()

        elif self.request.user.groups.filter(name='Team Leader Group').exists():
            employee_id = MyUser.objects.get(id=self.request.user.id)
            return employee_id.assignee.all()

        elif self.request.user.groups.filter(name='Low Level Employee Group').exists():
            employee_id = MyUser.objects.get(id=self.request.user.id)
            return employee_id.employer_model

        raise PermissionDenied


class ModuleCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    """
        Generic View to Create an module
    """
    permission_required = 'jira.add_module'
    raise_exception = True
    template_name = 'add_module.html'
    model = Module
    form_class = AddEditModuleForm
    success_url = reverse_lazy('module_list_view')

    # def get_form_kwargs(self):
    #     kwargs = super(AddEvent, self).get_form_kwargs()
    #
    # kwargs.update({'logged_user': self.request.user})
    # return kwargs

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'logged_user': self.request.user})
        return kwargs

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} created'.format(form.instance))
        return result


class ModuleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    """
        Generic View to Update an Module
    """
    permission_required = 'jira.change_module'
    raise_exception = True
    form_class = AddEditModuleForm
    template_name = 'update_module.html'
    model = Module
    success_url = reverse_lazy('module_list_view')

    def get(self, request, *args, **kwargs):

        if self.request.user.groups.filter(name='Team Leader Group').exists():
            self.object = self.get_object()
            employee_id = MyUser.objects.get(id=self.request.user.id)
            if self.object in employee_id.assignee.all():
                return super().get(request, *args, **kwargs)
            raise PermissionDenied

        elif self.request.user.groups.filter(name='Admin Group').exists():
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)

        raise PermissionDenied

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'logged_user': self.request.user})
        return kwargs

    # def get_context_data(self, **kwargs):
    #     """Insert the form into the context dict."""
    #     print(kwargs)
    #
    #     if 'form' not in kwargs:
    #         print(self.get_form())
    #         kwargs['form'] = self.get_form()
    #     return super().get_context_data(**kwargs)

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '{} updated'.format(form.instance))
        return result


class ModuleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    """
    Generic View to Delete an Module
    """
    permission_required = 'jira.delete_module'
    raise_exception = True
    template_name = 'delete_module.html'
    model = Module
    success_url = reverse_lazy('module_list_view')

    def get_success_url(self):
        if self.success_url:
            messages.warning(
                self.request, '{} deleted'.format(self.object.__dict__['module_name']))
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
