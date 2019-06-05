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
from tingweb import views, admin

users = []

admins = [
	url(r'adm/login/$', admin.AdminLogin.as_view(), name='ting_wb_adm_login'),
	url(r'adm/logout/$', admin.logout, name='ting_wb_adm_logout'),
	url(r'adm/welcome/$', admin.welcome_to_ting, name='ting_wb_adm_welcome'),
	url(r'adm/dashboard/$', admin.dashboard, name='ting_wb_adm_dashboard'),

	# Admin Reset Password

	url(r'adm/reset/password/submit/$', admin.submit_reset_password, name='ting_wb_adm_submit_reset_pwd'),
	url(r'adm/reset/password/link/(?P<token>[^/]+)/$', admin.reset_password_link, name='ting_wb_adm_reset_pwd_link'),
	url(r'adm/reset/password/reset/(?P<token>[^/]+)/$', admin.reset_password, name='ting_wb_adm_reset_pwd'),
	
	# Administrators

	url(r'adm/administrators/all/$', admin.administrators, name='ting_wb_adm_administrators'),
	url(r'adm/administrators/add/$', admin.add_new_admin, name='ting_wb_adm_add_new_admin'),
	url(r'adm/administrators/profile/load/(?P<token>[^/]+)/$', admin.load_admin_profile, name='ting_wb_adm_load_admin_profile'),
	url(r'adm/administrators/profile/edit/(?P<token>[^/]+)/$', admin.edit_admin_profile, name='ting_wb_adm_edit_admin_profile'),
	url(r'adm/administrators/profile/disable/toggle/(?P<token>[^/]+)/$', admin.disable_admin_account_toggle, name='ting_wb_adm_disable_admin_profile_toggle'),
	url(r'adm/administrators/permissions/edit/(?P<token>[^/]+)/$', admin.edit_admin_permissions, name='ting_wb_adm_edit_admin_permissions'),
	url(r'adm/administrators/permissions/update/(?P<token>[^/]+)/$', admin.update_admin_permissions, name='ting_wb_adm_update_admin_permissions'),
	
	# Admin Session

	url(r'adm/admin/profile/$', admin.admin_session, name='ting_wb_adm_admin_session'),
	url(r'adm/admin/profile/update/image/$', admin.update_admin_image, name='ting_wb_adm_admin_update_image'),
	url(r'adm/admin/profile/update/profile/(?P<token>[^/]+)/$', admin.update_admin_profile, name='ting_wb_adm_admin_update_profile'),
	url(r'adm/admin/security/$', admin.admin_security, name='ting_wb_adm_admin_security'),
	url(r'adm/admin/security/update/password/$', admin.update_admin_password, name='ting_wb_adm_admin_update_password'),
	url(r'adm/admin/permissions/$', admin.admin_permissions, name='ting_wb_adm_admin_permissions'),
	
	# Restaurant and Config

	url(r'adm/restaurant/key/activate/$', admin.activate_licence_key, name='ting_wb_adm_activate_licence_key'),
	url(r'adm/restaurant/about/$', admin.restaurant, name='ting_wb_adm_restaurant'),
	url(r'adm/restaurant/update/logo/$', admin.update_restaurant_logo, name='ting_wb_adm_restaurant_update_logo'),
	url(r'adm/restaurant/update/profile/$', admin.update_restaurant_profile, name='ting_wb_adm_restaurant_update_profile'),	
	url(r'adm/restaurant/update/config/$', admin.update_restaurant_config, name='ting_wb_adm_restaurant_update_config'),

	# Categories

	url(r'adm/categories/all/$', admin.categories, name='ting_wb_adm_categories'),
	url(r'adm/categories/add/new/$', admin.add_new_category, name='ting_wb_add_category'),
	url(r'adm/categories/delete/(?P<slug>[^/]+)/$', admin.delete_category, name='ting_wb_delete_category'),
	url(r'adm/categories/edit/(?P<slug>[^/]+)/$', admin.edit_category, name='ting_wb_edit_category'),
	url(r'adm/categories/update/(?P<slug>[^/]+)/$', admin.update_category, name='ting_wb_update_category'),

	# Menus	

	url(r'adm/menu/food/$', admin.menu_food, name='ting_wb_adm_menu_food'),
	url(r'adm/menu/drinks/$', admin.menu_drinks, name='ting_wb_adm_menu_drinks'),
	url(r'adm/menu/dishes/$', admin.menu_dishes, name='ting_wb_adm_menu_dishes'),

	# Menu Food

	url(r'adm/menu/food/add/new/$', admin.add_new_menu_food, name='ting_wb_adm_add_menu_food'),
	url(r'adm/menu/food/avail/toggle/(?P<food>\d+)/$', admin.avail_menu_food_toggle, name='ting_wb_adm_menu_food_avail_toggle'),
	url(r'adm/menu/food/move/type/(?P<food>\d+)/to/(?P<food_type_key>\d+)/$', admin.move_menu_food_to_type, name='ting_wb_adm_menu_food_move_to_type'),
	url(r'adm/menu/food/move/category/(?P<food>\d+)/to/(?P<category>\d+)/$', admin.move_menu_food_to_category, name='ting_wb_adm_menu_food_move_to_category'),
	url(r'adm/menu/food/edit/(?P<food>\d+)/$', admin.edit_menu_food, name='ting_wb_adm_menu_food_edit'),
	url(r'adm/menu/food/update/(?P<food>\d+)/$', admin.update_menu_food, name='ting_wb_adm_menu_food_update'),
	url(r'adm/menu/food/delete/(?P<food>\d+)/$', admin.delete_menu_food, name='ting_wb_adm_menu_food_delete'),
	url(r'adm/menu/food/update/(?P<food>\d+)/image/delete/(?P<image>\d+)/$', admin.delete_menu_food_image, name='ting_wb_adm_menu_food_delete_image'),
	url(r'adm/menu/food/load/(?P<food>\d+)/$', admin.load_menu_food, name='ting_wb_adm_menu_food_load'),

	# Menu Drink

	url(r'adm/menu/drink/add/new/$', admin.add_new_menu_drink, name='ting_wb_adm_add_menu_drink'),
	url(r'adm/menu/drink/avail/toggle/(?P<drink>\d+)/$', admin.avail_menu_drink_toggle, name='ting_wb_adm_menu_drink_avail_toggle'),
	url(r'adm/menu/drink/move/type/(?P<drink>\d+)/to/(?P<drink_type_key>\d+)/$', admin.move_menu_drink_to_type, name='ting_wb_adm_menu_drink_move_to_type'),
	url(r'adm/menu/drink/edit/(?P<drink>\d+)/$', admin.edit_menu_drink, name='ting_wb_adm_menu_drink_edit'),
	url(r'adm/menu/drink/update/(?P<drink>\d+)/$', admin.update_menu_drink, name='ting_wb_adm_menu_drink_update'),
	url(r'adm/menu/drink/delete/(?P<drink>\d+)/$', admin.delete_menu_drink, name='ting_wb_adm_menu_drink_delete'),
	url(r'adm/menu/drink/update/(?P<drink>\d+)/image/delete/(?P<image>\d+)/$', admin.delete_menu_drink_image, name='ting_wb_adm_menu_drink_delete_image'),
	url(r'adm/menu/drink/load/(?P<drink>\d+)/$', admin.load_menu_drink, name='ting_wb_adm_menu_drink_load'),

	# Menu Dish

	url(r'adm/menu/dish/add/new/$', admin.add_new_menu_dish, name='ting_wb_adm_add_menu_dish'),
	url(r'adm/menu/dish/avail/toggle/(?P<dish>\d+)/$', admin.avail_menu_dish_toggle, name='ting_wb_adm_menu_dish_avail_toggle'),
	url(r'adm/menu/dish/move/type/(?P<dish>\d+)/to/(?P<dish_time_key>\d+)/$', admin.move_menu_dish_to_type, name='ting_wb_adm_menu_dish_move_to_type'),
	url(r'adm/menu/dish/move/category/(?P<dish>\d+)/to/(?P<category>\d+)/$', admin.move_menu_dish_to_category, name='ting_wb_adm_menu_dish_move_to_category'),
	url(r'adm/menu/dish/edit/(?P<dish>\d+)/$', admin.edit_menu_dish, name='ting_wb_adm_menu_dish_edit'),
	url(r'adm/menu/dish/update/(?P<dish>\d+)/$', admin.update_menu_dish, name='ting_wb_adm_menu_dish_update'),
	url(r'adm/menu/dish/delete/(?P<dish>\d+)/$', admin.delete_menu_dish, name='ting_wb_adm_menu_dish_delete'),
	url(r'adm/menu/dish/update/(?P<dish>\d+)/image/delete/(?P<image>\d+)/$', admin.delete_menu_dish_image, name='ting_wb_adm_menu_dish_delete_image'),
	url(r'adm/menu/dish/drink/(?P<dish>\d+)/add/(?P<drink>\d+)/$', admin.add_drink_to_menu_dish, name='ting_wb_adm_menu_dish_add_drink'),
	url(r'adm/menu/dish/drink/(?P<dish>\d+)/remove/$', admin.remove_drink_to_menu_dish, name='ting_wb_adm_menu_dish_remove_drink'),
	url(r'adm/menu/dish/food/(?P<dish>\d+)/load/$', admin.load_menu_food_for_menu_dish, name='ting_wb_adm_menu_dish_food_load'),
	url(r'adm/menu/dish/food/(?P<dish>\d+)/update/$', admin.update_food_menu_for_dish_menu, name='ting_wb_adm_menu_dish_food_update'),
	url(r'adm/menu/dish/load/(?P<dish>\d+)/$', admin.load_menu_dish, name='ting_wb_adm_menu_dish_load'),

	# Tables

	url(r'adm/tables/all/$', admin.tables, name='ting_wb_adm_tables'),
]

urlpatterns = admins + users
