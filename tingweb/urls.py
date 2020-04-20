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


users = [
	
	# User Auth

	url(r'usr/login/$', views.login, name='ting_usr_login'),
	url(r'usr/signup/google/$', views.sign_up_with_google, name='ting_usr_google_sign_up'),
	url(r'usr/signup/email/$', views.sign_up_with_email, name='ting_usr_email_sign_up'),
	url(r'usr/reset/password/submit/$', views.submit_reset_password, name='ting_usr_submit_reset_password'),
	url(r'usr/reset/password/link/(?P<token>[^/]+)/$', views.reset_password_link, name='ting_usr_reset_pwd_link'),
	url(r'usr/reset/password/reset/(?P<token>[^/]+)/$', views.reset_password, name='ting_usr_reset_pwd'),
	url(r'usr/logout/$', views.logout, name='ting_usr_logout'),

	# User Data

	url(r'usr/profile/(?P<user>\d+)-(?P<username>[^/]+)/$', views.user_profile, name='ting_usr_profile'),
	url(r'usr/moments/(?P<user>\d+)-(?P<username>[^/]+)/$', views.user_moments, name='ting_usr_moments'),
	url(r'usr/restaurants/(?P<user>\d+)-(?P<username>[^/]+)/$', views.user_restaurants, name='ting_usr_restaurants'),
	url(r'usr/restaurants/load/(?P<user>\d+)/$', views.load_user_restaurants, name='ting_usr_load_restaurants'),
	url(r'usr/orders/(?P<user>\d+)-(?P<username>[^/]+)/$', views.user_orders, name='ting_usr_orders'),
	url(r'usr/bookings/(?P<user>\d+)-(?P<username>[^/]+)/$', views.user_bookings, name='ting_usr_bookings'),
	url(r'usr/reservation/load/(?P<user>\d+)/$', views.load_user_reservations, name='ting_usr_load_reservations'),
	url(r'usr/get/map/pin/(?P<user>\d+)/$', views.get_user_map_pin_svg, name='ting_usr_get_user_map_pin_svg'),

	# User Profile

	url(r'usr/profile/image/update/$', views.update_user_profile_image, name='ting_usr_update_image_profile'),
	url(r'usr/profile/email/update/$', views.update_user_email, name='ting_usr_update_email_profile'),
	url(r'usr/profile/password/update/$', views.update_user_password, name='ting_usr_update_password_profile'),
	url(r'usr/profile/info/private/update/$', views.update_user_private, name='ting_usr_update_private_profile'),
	url(r'usr/profile/info/public/update/$', views.update_user_public, name='ting_usr_update_public_profile'),
	url(r'usr/profile/address/add/$', views.add_user_address, name='ting_usr_add_address'),
	url(r'usr/profile/address/edit/(?P<address>\d+)/$', views.load_user_edit_address, name='ting_usr_edit_address'),
	url(r'usr/profile/address/update/(?P<address>\d+)/$', views.update_user_address, name='ting_usr_update_address'),
	url(r'usr/profile/address/delete/(?P<address>\d+)/$', views.delete_user_address, name='ting_usr_delete_address'),

	# Global

	url(r'usr/g/discovery/$', views.discovery, name='ting_usr_global_discovery'),
	url(r'usr/g/discovery/promotions/today/$', views.discover_today_promotions, name='ting_usr_global_discovery_today_promotions'),
	url(r'usr/g/discovery/cuisine/r/(?P<cuisine>\d+)-(?P<slug>[^/]+)/$', views.discover_cuisine_restaurants, name='ting_usr_global_discover_r_cuisine'),
	url(r'usr/g/discovery/cuisine/m/(?P<cuisine>\d+)-(?P<slug>[^/]+)/$', views.discover_cuisine_menus, name='ting_usr_global_discover_m_cuisine'),
	url(r'usr/g/restaurants/$', views.restaurants, name='ting_usr_global_restaurants'),
	url(r'usr/g/restaurants/filter/$', views.filter_restaurants_search, name='ting_usr_global_restaurants_filter'),
	url(r'usr/g/moments/$', views.moments, name='ting_usr_global_moments'),
	url(r'usr/g/blogs/$', views.blogs, name='ting_usr_global_blogs'),

	# Restaurant & Branch

	url(r'usr/restaurant/get/map/pin/(?P<restaurant>\d+)/html/$', views.get_restaurant_map_pin_html, name='ting_usr_restaurant_get_map_pin_html'),
	url(r'usr/restaurant/get/map/pin/(?P<restaurant>\d+)/svg/$', views.get_restaurant_map_pin_svg, name='ting_usr_restaurant_get_map_pin_svg'),
	url(r'usr/restaurant/get/map/pin/(?P<restaurant>\d+)/img/$', views.get_restaurant_map_pin_img, name='ting_usr_restaurant_get_map_pin_img'),
	url(r'usr/restaurant/like/toggle/(?P<restaurant>[^/]+)/(?P<branch>[^/]+)$', views.like_restaurant, name='ting_usr_like_restaurant_toggle'),
	url(r'usr/restaurant/like/load/(?P<restaurant>[^/]+)/(?P<branch>[^/]+)$', views.load_restaurant_likes, name='ting_usr_load_restaurant_likes'),
	url(r'usr/restaurant/load/menus/(?P<restaurant>[^/]+)/branch/top/five/(?P<branch>[^/]+)/$', views.load_branch_top_five, name='ting_usr_load_branch_top_five'),
	url(r'usr/restaurant/load/maps/(?P<restaurant>[^/]+)/directions/to/branch/(?P<branch>[^/]+)/$', views.load_branch_directions, name='ting_usr_load_branch_directions'),
	url(r'usr/restaurant/promos/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_promotions, name='ting_usr_get_restaurant_promotions'),
	url(r'usr/restaurant/foods/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_foods, name='ting_usr_get_restaurant_foods'),
	url(r'usr/restaurant/drinks/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_drinks, name='ting_usr_get_restaurant_drinks'),
	url(r'usr/restaurant/dishes/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_dishes, name='ting_usr_get_restaurant_dishes'),
	url(r'usr/restaurant/reviews/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_reviews, name='ting_usr_get_restaurant_reviews'),
	url(r'usr/restaurant/reviews/load/(?P<restaurant>\d+)-(?P<branch>\d+)/$', views.load_restaurant_reviews, name='ting_usr_load_restaurant_reviews'),
	url(r'usr/restaurant/reviews/add/(?P<restaurant>\d+)-(?P<branch>\d+)/$', views.add_restaurant_review, name='ting_usr_add_restaurant_review'),
	url(r'usr/restaurant/likes/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_likes, name='ting_usr_get_restaurant_likes'),
	url(r'usr/restaurant/about/(?P<restaurant>\d+)-(?P<branch>\d+)-(?P<slug>[^/]+)$', views.get_restaurant_about, name='ting_usr_get_restaurant_about'),
	url(r'usr/restaurant/menus/cus/(?P<branch>[^/]+)-(?P<cuisine>[^/]+)-(?P<slug>[^/]+)$', views.get_restaurant_menus_cuisine, name='ting_usr_get_restaurant_menus_cuisine'),
	url(r'usr/restaurant/menus/cat/(?P<branch>[^/]+)-(?P<category>[^/]+)-(?P<slug>[^/]+)$', views.get_restaurant_menus_category, name='ting_usr_get_restaurant_menus_category'),
	url(r'usr/restaurant/menus/rad/(?P<branch>[^/]+)/$', views.load_branch_menus_rand, name='ting_usr_load_branch_menus_rand'),

	# Menus & Promotions

	url(r'usr/menu/(?P<menu>\d+)-(?P<slug>[^/]+)$', views.get_menu, name='ting_usr_menu_get'),
	url(r'usr/promo/(?P<promotion>\d+)-(?P<slug>[^/]+)$', views.get_promotion, name='ting_usr_promotion_get'),
	url(r'usr/menu/like/toogle/(?P<menu>[^/]+)/$', views.like_menu, name='ting_usr_menu_like'),
	url(r'usr/promo/interest/toogle/(?P<promo>[^/]+)/$', views.interest_promotion, name='ting_usr_promotion_interest'),
	url(r'usr/menu/reviews/add/(?P<menu>\d+)/$', views.add_menu_review, name='ting_usr_menu_add_review'),
	url(r'usr/menu/reviews/load/(?P<menu>\d+)/$', views.load_menu_reviews, name='ting_usr_menu_load_reviews'),
	url(r'usr/menu/promotion/today/(?P<menu>[^/]+)/$', views.load_menu_today_promotion, name='ting_usr_load_menu_today_promotion'),

	# Reservation

	url(r'usr/reservation/make/resto/(?P<restaurant>\d+)/branch/(?P<branch>\d+)/$', views.make_reservation, name='ting_usr_make_reservation'),
	url(r'usr/reservation/edit/load/(?P<reservation>\d+)/$', views.load_edit_reservation, name='ting_usr_load_edit_reservation'),
	url(r'usr/reservation/update/(?P<reservation>\d+)/$', views.update_reservation, name='ting_usr_update_reservation'),
	url(r'usr/reservation/cancel/(?P<reservation>\d+)/$', views.cancel_reservation, name='ting_usr_cancel_reservation'),
]

admins = [
	
	# Auth & Login & Welcomw

	url(r'adm/signup/$', admin.signup_restaurant, name='ting_wb_resto_signup'),
	url(r'adm/login/$', admin.AdminLogin.as_view(), name='ting_wb_adm_login'),
	url(r'adm/logout/$', admin.logout, name='ting_wb_adm_logout'),
	url(r'adm/welcome/$', admin.welcome_to_ting, name='ting_wb_adm_welcome'),
	url(r'adm/dashboard/$', admin.dashboard, name='ting_wb_adm_dashboard'),

	# Admin Reset Password

	url(r'adm/reset/password/submit/$', admin.submit_reset_password, name='ting_wb_adm_submit_reset_pwd'),
	url(r'adm/reset/password/link/(?P<token>[^/]+)/$', admin.reset_password_link, name='ting_wb_adm_reset_pwd_link'),
	url(r'adm/reset/password/reset/(?P<token>[^/]+)/$', admin.reset_password, name='ting_wb_adm_reset_pwd'),

	# Branches
	
	url(r'adm/branches/all/$', admin.branches, name='ting_wb_adm_branches'),
	url(r'adm/branches/add/$', admin.add_new_branch, name='ting_wb_adm_add_branch'),
	url(r'adm/branches/avail/toogle/(?P<branch>\d+)/$', admin.avail_branch_toggle, name='ting_wb_avail_branch_toggle'),
	url(r'adm/branches/edit/(?P<branch>\d+)/$', admin.edit_branch, name='ting_wb_edit_branch'),
	url(r'adm/branches/update/(?P<branch>\d+)/$', admin.update_branch, name='ting_wb_update_branch'),
	url(r'adm/branches/load/(?P<branch>\d+)/$', admin.load_branch, name='ting_wb_load_branch'),

	# Administrators

	url(r'adm/administrators/all/$', admin.administrators, name='ting_wb_adm_administrators'),
	url(r'adm/administrators/add/$', admin.add_new_admin, name='ting_wb_adm_add_new_admin'),
	url(r'adm/administrators/profile/load/(?P<token>[^/]+)/$', admin.load_admin_profile, name='ting_wb_adm_load_admin_profile'),
	url(r'adm/administrators/profile/edit/(?P<token>[^/]+)/$', admin.edit_admin_profile, name='ting_wb_adm_edit_admin_profile'),
	url(r'adm/administrators/profile/disable/toggle/(?P<token>[^/]+)/$', admin.disable_admin_account_toggle, name='ting_wb_adm_disable_admin_profile_toggle'),
	url(r'adm/administrators/permissions/edit/(?P<token>[^/]+)/$', admin.edit_admin_permissions, name='ting_wb_adm_edit_admin_permissions'),
	url(r'adm/administrators/permissions/update/(?P<token>[^/]+)/$', admin.update_admin_permissions, name='ting_wb_adm_update_admin_permissions'),
	url(r'adm/administrators/move/(?P<token>[^/]+)/to/branch/(?P<branch>\d+)/$', admin.move_admin_to_branch, name='ting_wb_adm_move_admin_to_branch'),
	
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
	url(r'adm/restaurant/update/categories/$', admin.update_restaurant_categories, name='ting_wb_adm_update_restaurant_categories'),
	url(r'adm/restaurant/update/branch/profile/$', admin.update_branch_profile, name='ting_wb_adm_restaurant_update_branch_profile'),

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
	url(r'adm/menu/food/move/cuisine/(?P<food>\d+)/to/(?P<category>\d+)/$', admin.move_menu_food_to_cuisine, name='ting_wb_adm_menu_food_move_to_cuisine'),
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
	url(r'adm/menu/dish/move/cuisine/(?P<dish>\d+)/to/(?P<category>\d+)/$', admin.move_menu_dish_to_cuisine, name='ting_wb_adm_menu_dish_move_to_cuisine'),
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
	url(r'adm/tables/add/$', admin.add_new_table, name='ting_wb_adm_add_table'),
	url(r'adm/tables/edit/(?P<table>\d+)/$', admin.load_edit_table, name='ting_wb_adm_load_edit_table'),
	url(r'adm/tables/update/(?P<table>\d+)/$', admin.update_table, name='ting_wb_adm_update_table'),
	url(r'adm/tables/avail/toggle/(?P<table>\d+)/$', admin.avail_table_toggle, name='ting_wb_adm_avail_toggle_table'),
	url(r'adm/tables/waiter/(?P<waiter>\d+)/assign/(?P<table>\d+)/$', admin.assign_waiter_table, name='ting_wb_adm_assign_waiter_table'),
	url(r'adm/tables/waiter/remove/(?P<table>\d+)/$', admin.remove_waiter_table, name='ting_wb_adm_remove_waiter_table'),

	# Promotions

	url(r'adm/promotions/all/$', admin.promotions, name='ting_wb_adm_promotions'),
	url(r'adm/promotions/add/$', admin.add_new_promotion, name='ting_wb_adm_add_promotion'),
	url(r'adm/promotions/edit/(?P<promotion>\d+)/$', admin.load_edit_promotion, name='ting_wb_adm_edit_promotion'),
	url(r'adm/promotions/update/(?P<promotion>\d+)/$', admin.update_promotion, name='ting_wb_adm_update_promotion'),
	url(r'adm/promotions/avail/toggle/(?P<promotion>\d+)/$', admin.avail_promotion_toggle, name='ting_wb_adm_avail_promotion'),	
	url(r'adm/promotions/delete/(?P<promotion>\d+)/$', admin.delete_promotion, name='ting_wb_adm_delete_promotion'),
	url(r'adm/promotions/load/(?P<promotion>\d+)/$', admin.load_promotion, name='ting_wb_adm_load_promotion'),

	# Bookings

	url(r'adm/reservations/all/$', admin.reservations, name='ting_wb_adm_reservations'),
	url(r'adm/reservations/load/(?P<reservation>\d+)/$', admin.load_reservation, name='ting_wb_adm_load_reservation'),
	url(r'adm/reservations/accept/(?P<reservation>\d+)/$', admin.accept_reservation, name='ting_wb_adm_accept_reservation'),
	url(r'adm/reservations/decline/(?P<reservation>\d+)/$', admin.decline_reservation, name='ting_wb_adm_decline_reservation'),

	# Placements & Orders

	url(r'adm/placements/all/$', admin.placements, name='ting_wb_adm_placements'),
	url(r'adm/placements/load/all/$', admin.load_placements, name='ting_wb_adm_load_placements'),
	url(r'adm/placements/get/(?P<placement>\d+)/$', admin.load_user_placement, name='ting_wb_adm_load_user_placement'),
	url(r'adm/placements/messages/load/all/$', admin.load_admin_messages, name='ting_wb_adm_load_messages'),
	url(r'adm/placements/messages/(?P<message>\d+)/delete/$', admin.delete_admin_message, name='ting_wb_adm_delete_message'),
	url(r'adm/placements/messages/load/count/$', admin.get_admin_messages_count, name='ting_wb_adm_get_messages_count'),
	url(r'adm/placements/dashboard/load/all/$', admin.load_placements_dashboard, name='ting_wb_adm_load_placements_dashboard'),
	url(r'adm/placements/(?P<token>[^/]+)/done/$', admin.done_placement, name='ting_wb_adm_done_placement'),
	url(r'adm/placements/(?P<token>[^/]+)/assign/waiter/(?P<waiter>\d+)/$', admin.assign_waiter_placement, name='ting_wb_adm_assign_waiter_placement'),
	url(r'adm/placements/(?P<placement>\d+)/bill/mark/paid/$', admin.mark_bill_paid, name='ting_wb_adm_mark_bill_paid'),
	url(r'adm/orders/dashboard/load/all/$', admin.load_orders_dashboard, name='ting_wb_adm_load_orders_dashboard'),
	url(r'adm/orders/(?P<order>\d+)/load/$', admin.load_user_placement_order, name='ting_wb_adm_load_user_placement_order'),
	url(r'adm/orders/(?P<order>\d+)/accept/$', admin.accept_user_order, name='ting_wb_adm_accept_user_order'),
	url(r'adm/orders/(?P<order>\d+)/decline/$', admin.decline_user_order, name='ting_wb_adm_decline_user_order'),
	url(r'adm/orders/extras/(?P<placement>\d+)/add/$', admin.add_bill_extra, name='ting_wb_adm_add_bill_extra'),
	url(r'adm/orders/extras/(?P<extra>\d+)/delete/$', admin.delete_bill_extra, name='ting_wb_adm_delete_bill_extra'),
]

urlpatterns = admins + users
