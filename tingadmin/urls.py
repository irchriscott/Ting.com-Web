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
from tingadmin import views

urlpatterns = [
    url(r'login/$', views.AdminLogin.as_view(), name='ting_admin_login'),
    url(r'logout/$', views.logout, name='ting_admin_logout'),
    url(r'dashboard/$', views.dashboard, name='ting_admin_dashboard'),
    url(r'restaurants/$', views.restaurants, name='ting_admin_restaurants'),
    url(r'restaurants/admin/add/$', views.add_restaurant, name='ting_admin_add_restaurant'),
    url(r'categories/$', views.categories, name='ting_admin_categories'),
    url(r'categories/add/$', views.add_category, name='ting_admin_add_category'),
    url(r'categories/(?P<id>\d+)/delete/$', views.delete_category, name='ting_admin_delete_category'),
    url(r'packages/$', views.packages, name='ting_admin_packages'),
    url(r'packages/add/$', views.add_package, name='ting_admin_add_package')
]
