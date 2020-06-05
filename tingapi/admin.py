# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse, request
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count, Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.backend import AdminAuthentication
from tingweb.mailer import (
							SendAdminRegistrationMail, SendAdminResetPasswordMail, SendAdminSuccessResetPasswordMail,
							SendAcceptedReservationMail, SendDeclinedReservationMail
							)
from tingweb.models import (
                                Restaurant, User, Branch, UserRestaurant, Menu, MenuLike, MenuReview, Promotion, 
                                PromotionInterest, RestaurantReview, Booking, Food, Drink, Dish, RestaurantTable, 
                                Placement, Order, Bill, BillExtra, PlacementMessage, Administrator, FoodCategory
                            )
from tingadmin.models import RestaurantCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from datetime import datetime, timedelta, date
from background_task import background
import tingweb.admin as admin
import tingadmin.permissions as perm
import ting.utils as utils
import random
import decimal
import json
import imgkit
import os
import re


pnconfig = PNConfiguration()
pnconfig.subscribe_key = utils.PUBNUB_SUBSCRIBE_KEY
pnconfig.publish_key = utils.PUBNUB_PUBLISH_KEY

pubnub = PubNub(pnconfig)


def ting_publish_callback(envelope, status):
    pass


def check_admin_login(func):
	def wrapper(request, *args, **kwargs):
		token = request.META.get('HTTP_AUTHORIZATION')
		try:
			admin = Administrator.objects.filter(token=token).first()
			if admin != None:
				request.session['admin'] = admin.pk
			else:
				return HttpJsonResponse(ResponseObject('error', 'Mismatch Token !!!', 401))
		except Administrator.DoesNotExist:
			return HttpJsonResponse(ResponseObject('error', 'Mismatch Token !!!', 401))

		return func(request, *args, **kwargs)
	wrapper.__doc__ = func.__doc__
	wrapper.__name__ = func.__name__
	return wrapper


def is_admin_enabled(func):
	def wrapper(request, *args, **kwargs):
		admin = Administrator.objects.get(pk=request.session['admin'])
		if admin.is_disabled == True:
			return HttpJsonResponse(ResponseObject('error', 'Sorry, Your Account Has Been Disabled !!!', 401))
		return func(request, *args, **kwargs)
	wrapper.__doc__ = func.__doc__
	wrapper.__name__ = func.__name__
	return wrapper


def has_admin_permissions(permission=None, xhr=None):
	def decorator_wrapper(func):
		def wrapper(request, *args, **kwargs):
			if 'admin' in request.session:
				admin = Administrator.objects.get(pk=request.session['admin'])
				if type(permission) == list:
					if any((True for p in permission if p in admin.permissions)) == False:
						return HttpJsonResponse(ResponseObject('error', 'Permission Denied !!!', 401))
				else:
					if admin.has_permission(permission) == False:
						return HttpJsonResponse(ResponseObject('error', 'Permission Denied !!!', 401))
	        
			return func(request, *args, **kwargs)
	    
		wrapper.__doc__ = func.__doc__
		wrapper.__name__ = func.__name__
		return wrapper
	
	return decorator_wrapper


@csrf_exempt
def api_sign_up_with_google(request):

	token = request.POST.get('token')
	email = request.POST.get('email')

	token_id = token.split('-')[0]
	link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_wb_adm_login')
	
	try:
		check_admin = Administrator.objects.get(email=email)
		if check_admin.token.split('-')[0] == token_id:
			try:
				if len(check_admin.token.split('-')[1]) < 128:
					check_admin.token = '%s-%s' %(check_admin.token.split('-')[0], get_random_string(512))
					check_admin.updated_at = timezone.now()
					check_admin.save()
			except KeyError as e:
				pass
                    
			request.session['admin'] = check_admin.pk
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=check_admin.to_json_admin))
		else:
			check_admin.token = token
			check_admin.updated_at = timezone.now()
			check_admin.save()
			request.session['admin'] = check_admin.pk
                    
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=check_admin.to_json_admin, msgs=[]))
	
	except Administrator.DoesNotExist:
		return HttpJsonResponse(ResponseObject('error', 'Unknown Administrator Email', 405))


@csrf_exempt
def api_login(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')

		auth = AdminAuthentication(email=email, password=password)

		if auth.authenticate != None:
			request.session['admin'] = auth.authenticate.pk
			link = reverse('ting_wb_adm_dashboard')
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=auth.authenticate.to_json_admin, msgs=[]))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Invalid Email or Password !!!', 404))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@csrf_exempt
def api_submit_reset_password(request):
	return admin.submit_reset_password(request)


# RESTAURANT


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant', xhr='ajax')
def api_update_restaurant_profile(request):
	return admin.update_restaurant_profile(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant', xhr='ajax')
def api_update_restaurant_logo(request):
	return admin.update_restaurant_logo(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant', xhr='ajax')
def api_update_restaurant_categories(request):
	return admin.update_restaurant_categories(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_branch', xhr='ajax')
def api_update_branch_profile(request):
	return admin.update_branch_profile(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_configurations', xhr='ajax')
def api_update_restaurant_config(request):
	return admin.update_restaurant_config(request)


# ADMINISTRATOR


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_view_admin', 'can_view_all_admin'])
@require_http_methods(['GET'])
def api_administrators(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	administrators = Administrator.objects.filter(restaurant__pk=admin.pk).order_by('name') if admin.has_permission('can_view_all_admin') else Administrator.objects.filter(restaurant__pk=admin.pk, branch__pk=admin.branch.pk).order_by('name')
	return HttpResponse(json.dumps([admin.to_json_admin for admin in administrators], default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_view_admin', 'can_view_all_admin'])
@require_http_methods(['GET'])
def api_waiters(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	waiters = Administrator.objects.filter(restaurant__pk=admin.pk, branch__pk=admin.branch.pk, admin_type=4).order_by('name')
	return HttpResponse(json.dumps([waiter.to_json_s for waiter in waiters], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_admin', xhr='ajax')
def api_add_new_admin(request):
	return admin.add_new_admin(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def api_update_admin_profile(request, token):
	return admin.update_admin_profile(request, token)


@csrf_exempt
@check_admin_login
@is_admin_enabled
def api_update_admin_profile_image(request):
	return admin.update_admin_image(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def api_get_admin_session_profile(request):
	return HttpResponse(json.dumps(Administrator.objects.get(pk=request.session['admin']).to_json_admin, default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
def api_update_admin_password(request):
	return admin.update_admin_password(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_disable_admin', xhr='ajax')
def api_disable_admin_account_toggle(request, token):
	return admin.disable_admin_account_toggle(request, token)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def api_update_admin_permissions(request, token):
	return admin.update_admin_permissions(request, token)


# GLOBAL


def api_get_permission_list(request):
	return HttpResponse(json.dumps(perm.permissions, default=str), content_type='application/json')


def api_get_restaurant_categories(request):
	return HttpResponse(json.dumps([category.to_json for category in RestaurantCategory.objects.all()], default=str), content_type='application/json')


# BRANCHES


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_branch', xhr='ajax')
def api_branches(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk).order_by('-created_at')
	return HttpResponse(json.dumps([branch.to_json_admin_s for branch in branches], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_branch', xhr='ajax')
def api_add_new_branch(request):
	return admin.add_new_branch(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_branch', xhr='ajax')
def api_avail_branch_toggle(request, branch):
	return admin.avail_branch_toggle(request, branch)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_branch', xhr='ajax')
def api_update_branch(request, branch):
	return admin.update_branch(request, branch)


# CATEGORIES


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_category', xhr='ajax')
def api_categories(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	return HttpResponse(json.dumps([category.to_json for category in categories], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_category', xhr='ajax')
def api_add_new_category(request):
	return admin.add_new_category(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_category', xhr='ajax')
def api_update_category(request, category):
	category = FoodCategory.objects.get(pk=category)
	return admin.update_category(request, category.slug)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_category', xhr='ajax')
def api_delete_category(request, category):
	category = FoodCategory.objects.get(pk=category)
	return admin.delete_category(request, category.slug)


# TABLES


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_table', xhr='ajax')
def api_tables(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	tables = RestaurantTable.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk)
	return HttpResponse(json.dumps([table.to_json_admin for table in tables], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_table', xhr='ajax')
def api_add_new_table(request):
	return admin.add_new_table(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_table', xhr='ajax')
def api_avail_table_toggle(request, table):
	return admin.avail_table_toggle(request, table)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def api_update_table(request, table):
	return admin.update_table(request, table)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def api_assign_waiter_table(request, waiter, table):
	return admin.assign_waiter_table(request, waiter, table)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def api_remove_waiter_table(request, table):
	return admin.remove_waiter_table(request, table)


# RESERVATIONS


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_booking')
def api_date_reservations(request):
	dt = date.today() if request.GET.get('date') == None or request.GET.get('date') == '' else datetime.strptime(request.GET.get('date'), '%Y-%m-%d')
	admin = Administrator.objects.get(pk=request.session['admin'])
	bookings = Booking.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, date=dt).exclude(status=1).order_by('-updated_at')
	return HttpResponse(json.dumps([booking.to_json_admin for booking in bookings], default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_booking')
def api_new_reservations(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	bookings = Booking.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, status=1).order_by('-updated_at')
	return HttpResponse(json.dumps([booking.to_json_admin for booking in bookings], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_accept_booking', 'can_cancel_booking'])
def api_accept_reservation(request, reservation):
	return admin.accept_reservation(request, reservation)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_accept_booking', 'can_cancel_booking'])
def api_decline_reservation(request, reservation):
	return admin.decline_reservation(request, reservation)


# MENU ALL


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def api_menus_all(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	menus = Menu.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	return HttpResponse(json.dumps([menu.to_json_admin for menu in menus], default=str), content_type='application/json')


# MENU FOOD


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def api_menu_food(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	foods = Food.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	return HttpResponse(json.dumps([food.to_json_admin for food in foods], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu')
def api_add_new_menu_food(request):
	return admin.add_new_menu_food(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu')
def api_avail_menu_food_toggle(request, food):
	return admin.avail_menu_food_toggle(request, food)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_move_menu_food_to_type(request, food, food_type_key):
	return admin.move_menu_food_to_type(request, food, food_type_key)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_move_menu_food_to_category(request, food, category):
	return admin.move_menu_food_to_category(request, food, category)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_move_menu_food_to_cuisine(request, food, category):
	return admin.move_menu_food_to_cuisine(request, food, category)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_update_menu_food(request, food):
	return admin.update_menu_food(request, food)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_delete_menu_food_image(request, food, image):
	return admin.delete_menu_food_image(request, food, image)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu')
def api_delete_menu_food(request, food):
	return admin.delete_menu_food(request, food)


# MENU DRINK


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def api_menu_drink(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	drinks = Drink.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	return HttpResponse(json.dumps([drink.to_json_admin for drink in drinks], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu')
def api_add_new_menu_drink(request):
	return admin.add_new_menu_drink(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu')
def api_avail_menu_drink_toggle(request, drink):
	return admin.avail_menu_drink_toggle(request, drink)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def api_move_menu_drink_to_type(request, drink, drink_type_key):
	return admin.move_menu_drink_to_type(request, drink, drink_type_key)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_update_menu_drink(request, drink):
	return admin.update_menu_drink(request, drink)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_delete_menu_drink_image(request, drink, image):
	return admin.delete_menu_drink_image(request, drink, image)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu')
def api_delete_menu_drink(request, drink):
	return admin.delete_menu_drink(request, drink)


# MENU DISH


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def api_menu_dish(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dishes = Dish.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	return HttpResponse(json.dumps([dish.to_json_admin for dish in dishes], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu')
def api_add_new_menu_dish(request):
	return admin.add_new_menu_dish(request)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu')
def api_avail_menu_dish_toggle(request, dish):
	return admin.avail_menu_dish_toggle(request, dish)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_move_menu_dish_to_type(request, dish, dish_time_key):
	return admin.move_menu_dish_to_type(request, dish, dish_time_key)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_move_menu_dish_to_category(request, dish, category):
	return admin.move_menu_dish_to_category(request, dish, category)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def api_move_menu_dish_to_cuisine(request, dish, category):
	return admin.move_menu_dish_to_cuisine(request, dish, category)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_update_menu_dish(request, dish):
	return admin.update_menu_dish(request, dish)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_delete_menu_dish_image(request, dish, image):
	return admin.delete_menu_dish_image(request, dish, image)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu')
def api_delete_menu_dish(request, dish):
	return admin.delete_menu_dish(request, dish)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu')
def api_add_drink_to_menu_dish(request, dish, drink):
	return admin.add_drink_to_menu_dish(request, dish, drink)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def api_remove_drink_to_menu_dish(request, dish):
	return admin.remove_drink_to_menu_dish(request, dish)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def api_update_food_menu_for_dish_menu(request, dish):
	return admin.update_food_menu_for_dish_menu(request, dish)


# PROMOTIONS


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_promotion')
def api_promotions(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	promotions = Promotion.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	return HttpResponse(json.dumps([promotion.to_json_admin for promotion in promotions], default=str), content_type='application/json')


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_promotion', xhr='ajax')
def api_add_new_promotion(request):
	return admin.add_new_promotion(request)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_promotion', xhr='ajax')
def api_update_promotion(request, promotion):
	return admin.update_promotion(request, promotion)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_promotion', xhr='ajax')
def api_avail_promotion_toggle(request, promotion):
	return admin.avail_promotion_toggle(request, promotion)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_promotion', xhr='ajax')
def api_delete_promotion(request, promotion):
	return admin.delete_promotion(request, promotion)


# PLACEMENT


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements', xhr='ajax')
def api_placements(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	if admin.admin_type == '4':
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, waiter=admin.pk, is_done=False).order_by('-created_at')
	else:
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, is_done=False).order_by('-created_at')

	return HttpResponse(json.dumps([placement.to_admin_json_s for placement in placements], default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_done_placement', xhr='ajax')
def api_done_placement(request, token):
	return admin.done_placement(request, token)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_assign_table', xhr='ajax')
def api_assign_waiter_placement(request, token, waiter):
	return assign_waiter_placement(request, token, waiter)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_done_placement')
def api_mark_bill_paid(request, placement):
	return admin.mark_bill_paid(request, placement)


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements', xhr='ajax')
def api_get_placement(request, token):
	admin = Administrator.objects.get(pk=request.session['admin'])
	placement = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk, token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()

	if bill != None:

		orders = Order.objects.filter(bill__pk=placement.bill.pk, is_declined=False) if placement.bill != None else QuerySet([])
		extras = BillExtra.objects.filter(bill__placement_id=placement.pk) if placement.bill != None else QuerySet([])

		total_amount = 0
		for order in orders: 
			total_amount = total_amount + (order.price * order.quantity) if order.is_delivered == True else total_amount + 0

		extras_total = 0
		for extra in extras:
			extras_total = extras_total + (extra.quantity * extra.price)

		bill.amount = total_amount
		bill.extras_total = extras_total
		bill.total = total_amount + extras_total + bill.tips - ((total_amount * bill.discount) / 100)
		bill.save()

	return HttpResponse(json.dumps(placement.to_admin_json, default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
def api_load_bill_orders(request, token):
	admin = Administrator.objects.get(pk=request.session['admin'])
	placement = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk, token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()
	return HttpResponse(json.dumps([order.to_admin_json for order in Order.objects.filter(bill__pk=bill.pk, is_declined=False)] if bill != None else [], default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_accept_orders')
def api_accept_user_order(request, order):
	return admin.accept_user_order(request, order)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_accept_orders')
def api_decline_user_order(request, order):
	return admin.decline_user_order(request, order)


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements')
def api_add_bill_extra(request, placement):
	return admin.add_bill_extra(request, placement)


@check_admin_login
@is_admin_enabled
def api_delete_bill_extra(request, extra):
	return admin.delete_bill_extra(request, extra)