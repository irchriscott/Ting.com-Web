"""ting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from tingapi import views

urlpatterns = [
	url(r'usr/check/email-username/$', views.api_check_user_email_username),
	url(r'usr/signup/email/$', views.api_sign_up_with_email),
	url(r'usr/signup/google/$', views.api_sign_up_with_google),
	url(r'usr/auth/login/$', views.api_login),
	url(r'usr/auth/password/reset/$', views.api_submit_reset_password)
]