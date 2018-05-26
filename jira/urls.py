from django.urls import path
from django.contrib.auth.views import logout
from .views import (EmployeeView, EmployeeUpdateView, EmployeeDeleteView,  # EmployeeCreateView
                    ProjectView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
                    ModuleView, ModuleCreateView, ModuleDeleteView, ModuleUpdateView,
                    company_view, add_company, update_company, delete_company,
                    register)


urlpatterns = [

    path('', view=company_view, name='company_list_view'),
    path('add/', view=add_company, name='add_company'),
    path('update/<int:company_id>', view=update_company, name='update'),
    path('delete/<int:company_id>', view=delete_company, name='delete'),

    path('employee/', view=EmployeeView.as_view(), name='employee_list_view'),
    # path('employee/add/', view=EmployeeCreateView.as_view(), name='add_employee'),
    path('employee/update/<int:pk>/', view=EmployeeUpdateView.as_view(), name='update_employee'),
    path('employee/delete/<int:pk>/', view=EmployeeDeleteView.as_view(), name='delete_employee'),

    path('projects/', view=ProjectView.as_view(), name='project_list_view'),
    path('projects/add/', view=ProjectCreateView.as_view(), name='add_project'),
    path('projects/update/<int:pk>/', view=ProjectUpdateView.as_view(), name='update_project'),
    path('projects/delete/<int:pk>/', view=ProjectDeleteView.as_view(), name='delete_project'),

    path('modules/', view=ModuleView.as_view(), name='module_list_view'),
    path('modules/add/', view=ModuleCreateView.as_view(), name='add_module'),
    path('modules/update/<int:pk>/', view=ModuleUpdateView.as_view(), name='update_module'),
    path('modules/delete/<int:pk>/', view=ModuleDeleteView.as_view(), name='delete_module'),

    path('register/', view=register, name='register'),
    path('logout/', logout, {'template_name': 'logout.html'}, name='logout'),  # 'login' path in main urls.py
]
