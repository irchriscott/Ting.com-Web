from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class UserAuthentication(object):

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.admin = None
    
    def check_email(self):
        try:
            self.admin = User.objects.get(email=self.email)
        except User.DoesNotExist:
            pass
    
    def check_pswd(self):
        self.check_email()
        if self.admin != None:
            return self.admin if check_password(self.password, self.admin.password) == True else None
        else:
            return None

    @property
    def authenticate(self):
        return self.check_pswd()