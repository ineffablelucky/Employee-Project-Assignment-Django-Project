from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import (login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jira/', include('jira.urls')),
    path('login/', login, {'template_name': 'login.html'}, name='login'),
]
