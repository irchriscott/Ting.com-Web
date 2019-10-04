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

	# AUTH & USER

	url(r'usr/check/email-username/$', views.api_check_user_email_username),
	url(r'usr/signup/email/$', views.api_sign_up_with_email),
	url(r'usr/signup/google/$', views.api_sign_up_with_google),
	url(r'usr/auth/login/$', views.api_login),
	url(r'usr/auth/password/reset/$', views.api_submit_reset_password),
	url(r'usr/profile/image/update/$', views.api_update_user_profile_image),
	url(r'usr/profile/email/update/$', views.api_update_user_email),
	url(r'usr/profile/password/update/$', views.api_update_user_password),
	url(r'usr/profile/identity/update/$', views.api_update_user_identity),
	url(r'usr/profile/address/add/$', views.api_add_user_address),
	url(r'usr/profile/address/delete/(?P<address>\d+)/$', views.api_delete_user_address),
	url(r'usr/profile/address/update/(?P<address>\d+)/$', views.api_update_user_address),

	# RESTAURANT

	url(r'usr/g/restaurants/all/$', views.api_restaurants),
	url(r'usr/g/restaurants/promotions/(?P<branch>\d+)/$', views.api_load_restaurant_promotions, name='api_restaurant_promotions'),
	url(r'usr/g/restaurants/foods/(?P<branch>\d+)/$', views.api_load_restaurant_foods, name='api_restaurant_foods'),
	url(r'usr/g/restaurants/drinks/(?P<branch>\d+)/$', views.api_load_restaurant_drinks, name='api_restaurant_drinks'),
	url(r'usr/g/restaurants/dishes/(?P<branch>\d+)/$', views.api_load_restaurant_dishes, name='api_restaurant_dishes'),
	url(r'usr/g/restaurants/reviews/(?P<branch>\d+)/$', views.api_load_restaurant_reviews, name='api_restaurant_reviews'),
	url(r'usr/g/restaurants/likes/(?P<branch>\d+)/$', views.api_load_restaurant_likes, name='api_restaurant_likes'),

	# MENU

	url(r'usr/restaurant/menu/(?P<menu>\d+)/$', views.api_get_menu, name='api_restaurant_menu_get'),
	url(r'usr/menu/like/toogle/(?P<menu>\d+)/$', views.api_like_menu, name='api_restaurant_menu_like'),
	url(r'usr/menu/reviews/(?P<menu>\d+)/$', views.api_load_menu_reviews, name='api_restaurant_menu_reviews'),
	url(r'usr/menu/reviews/add/(?P<menu>\d+)/$', views.api_add_menu_review, name='api_restaurant_menu_add_review')

]