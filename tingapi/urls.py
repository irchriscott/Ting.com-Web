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

	url(r'usr/profile/get/(?P<user>\d+)/$', views.api_user_get, name='api_user_get'),
	url(r'usr/profile/get/auth/$', views.api_user_get_auth, name='api_user_get_auth'),
	url(r'usr/profile/map/pin/(?P<user>\d+)/$', views.api_user_map_pin),

	# RESTAURANT

	url(r'usr/g/restaurants/all/$', views.api_restaurants),
	url(r'usr/g/restaurants/search/filter/$', views.api_filter_restaurants),
	url(r'usr/g/restaurants/get/(?P<branch>\d+)/$', views.api_get_restaurant, name='api_restaurant_get_top_menus'),
	url(r'usr/g/restaurants/get/(?P<branch>\d+)/menus/top/$', views.api_restaurant_top_menus, name='api_restaurant_get'),
	url(r'usr/g/restaurants/promotions/(?P<branch>\d+)/$', views.api_load_restaurant_promotions, name='api_restaurant_promotions'),
	url(r'usr/g/restaurants/foods/(?P<branch>\d+)/$', views.api_load_restaurant_foods, name='api_restaurant_foods'),
	url(r'usr/g/restaurants/drinks/(?P<branch>\d+)/$', views.api_load_restaurant_drinks, name='api_restaurant_drinks'),
	url(r'usr/g/restaurants/dishes/(?P<branch>\d+)/$', views.api_load_restaurant_dishes, name='api_restaurant_dishes'),
	url(r'usr/g/restaurants/reviews/(?P<branch>\d+)/$', views.api_load_restaurant_reviews, name='api_restaurant_reviews'),
	url(r'usr/g/restaurants/reviews/add/(?P<branch>\d+)/$', views.api_add_restaurant_review, name='api_add_restaurant_review'),
	url(r'usr/g/restaurants/reviews/check/$', views.api_check_restaurant_review, name='api_restaurant_check_review'),
	url(r'usr/g/restaurants/like/toggle/(?P<branch>\d+)/$', views.api_like_restaurant, name='api_like_restaurant'),
	url(r'usr/g/restaurants/likes/(?P<branch>\d+)/$', views.api_load_restaurant_likes, name='api_restaurant_likes'),
	url(r'usr/g/restaurants/map/pin/(?P<branch>\d+)/$', views.api_restaurant_map_pin),
	url(r'usr/g/restaurants/filters/$', views.api_get_restaurant_filters),

	# MENU

	url(r'usr/restaurant/menu/(?P<menu>\d+)/$', views.api_get_menu, name='api_restaurant_menu_get'),
	url(r'usr/menu/like/toogle/(?P<menu>\d+)/$', views.api_like_menu, name='api_restaurant_menu_like'),
	url(r'usr/menu/reviews/(?P<menu>\d+)/$', views.api_load_menu_reviews, name='api_restaurant_menu_reviews'),
	url(r'usr/menu/reviews/add/(?P<menu>\d+)/$', views.api_add_menu_review, name='api_restaurant_menu_add_review'),
	url(r'usr/menu/reviews/check/$', views.api_check_menu_review, name='api_restaurant_menu_check_review'),

	# PROMOTION

	url(r'usr/menu/promotion/get/(?P<promo>\d+)/$', views.api_get_promotion, name='api_promotion_get'),
	url(r'usr/menu/promotion/interest/(?P<promo>\d+)/$', views.api_interest_promotion, name='api_promotion_interest'),
	url(r'usr/menu/promotion/get/(?P<promo>\d+)/menus/promoted/$', views.api_promotion_promoted_menus, name='api_promotion_get_promoted_menus'),

	# CUISINES

	url(r'usr/g/cuisines/all/$', views.api_get_cuisines),
	url(r'usr/g/cuisine/r/(?P<cuisine>\d+)/$', views.api_get_cuisine_restaurants),
	url(r'usr/g/cuisine/m/(?P<cuisine>\d+)/$', views.api_get_cuisine_menus),

	# DISCOVER

	url(r'usr/d/restaurants/$', views.api_get_discover_restaurants),
	url(r'usr/d/restaurants/top/$', views.api_get_top_restaurants),
	url(r'usr/d/today/promotions/rand/$', views.api_get_today_promotions_rand),
	url(r'usr/d/today/promotions/all/$', views.api_get_today_promotions_all),
	url(r'usr/d/menus/top/$', views.api_get_top_menus),
	url(r'usr/d/menus/discover/$', views.api_get_discover_menus),

	# PLACEMENT & ORDERS

	url(r'usr/po/table/request/$', views.api_request_table_restaurant),
	url(r'usr/po/placement/get/$', views.api_get_placement),
	url(r'usr/po/placement/people/update/$', views.api_update_people_placement),
	url(r'usr/po/orders/branch/menus/$', views.api_get_restaurant_menu_orders),
	url(r'usr/po/orders/menu/place/$', views.api_place_order_menu),
	url(r'usr/po/placement/orders/all/$', views.api_get_placement_menu_orders),
	url(r'usr/po/placement/order/(?P<order>\d+)/re/place/$', views.api_re_place_order_menu),
	url(r'usr/po/placement/order/(?P<order>\d+)/cancel/$', views.api_cancel_order_menu),
	url(r'usr/po/placement/bill/$', views.api_get_placement_bill),
	url(r'usr/po/placement/bill/tips/update/$', views.api_placement_bill_update_tips),
	url(r'usr/po/placement/bill/complete/$', views.api_placement_bill_conplete),
	url(r'usr/po/placement/bill/request/$', views.api_placement_bill_request),
	url(r'usr/po/placement/request/send/$', views.api_send_waiter_request),
	url(r'usr/po/placement/terminate/$', views.api_end_placement),
]