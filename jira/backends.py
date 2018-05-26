from django.contrib.auth.backends import ModelBackend
from .models import MyUser

# https://stackoverflow.com/questions/37332190/django-login-with-email
# https://stackoverflow.com/questions/44972983/allowing-both-email-and-username-login-in-django-project
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#authentication-backends


# AUTHENTICATION_BACKENDS = ['jira.backends.EmailBackend'] in settings.py

# https://github.com/django/django/blob/master/django/contrib/auth/backends.py
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(MyUser.USERNAME_FIELD)
        try:
            user = MyUser._default_manager.get_by_natural_key(username)
        except MyUser.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            MyUser().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = MyUser._default_manager.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
