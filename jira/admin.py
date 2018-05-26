from django.contrib import admin
from .models import Company, Employee, Project, Module, MyUser
from django.contrib.auth.admin import UserAdmin

admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(Module)


class MyUserAdmin(UserAdmin):  # to show extra details in admin panel instead of just object name
    list_display = ('email', 'full_name', 'designation', 'username', 'is_staff')


admin.site.register(MyUser, MyUserAdmin)
