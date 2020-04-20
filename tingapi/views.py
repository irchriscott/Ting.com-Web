# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse, request
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count, Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.backend import UserAuthentication
from tingweb.mailer import SendUserResetPasswordMail, SendUserUpdateEmailMail, SendUserSuccessResetPasswordMail
from tingweb.models import (
                                Restaurant, User, UserResetPassword, UserAddress, Branch, UserRestaurant, Menu,
                                MenuLike, MenuReview, Promotion, PromotionInterest, RestaurantReview, Booking,
                                Food, Drink, Dish, RestaurantTable, Placement, Order, Bill, BillExtra, PlacementMessage,
                                Moment, MomentMedia
                            )
from tingweb.forms import (
                                GoogleSignUpForm, UserLocationForm, EmailSignUpForm, UserImageForm, MenuReviewForm,
                                RestaurantReviewForm, ReservationForm
                            )
from tingapi.forms import MomentMediaForm
from tingadmin.models import RestaurantCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from datetime import datetime, timedelta, date
from background_task import background
import tingweb.views as web
import ting.utils as utils
import operator
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


@csrf_exempt
def api_check_user_email_username(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		username = request.POST.get('username')
		name = request.POST.get('name')

		if email == None or username == None or name == None or email == '' or username == '' or name == '':
			return HttpJsonResponse(ResponseObject('error', 'Please, Fill All The Fields', 406))

		check_email = User.objects.filter(email=email).count()
		check_username = User.objects.filter(username=username).count()

		if check_email > 0:
			return HttpJsonResponse(ResponseObject('error', 'Email Address Already Taken', 406))

		if check_username > 0:
			return HttpJsonResponse(ResponseObject('error', 'Username Already Taken', 406))

		return HttpJsonResponse(ResponseObject('success', 'Good To Go', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# USER && AUTH


def authenticate_user(xhr=None):
	def decorator_wrapper(func):
		def wrapper(request, *args, **kwargs):
			token = request.META.get('HTTP_AUTHORIZATION')
			try:
				user = User.objects.filter(token=token).first()
				if user != None:
					request.session['user'] = user.pk
				else:
					return HttpJsonResponse(ResponseObject('error', 'Mismatch Token !!!', 401))
			except User.DoesNotExist:
				return HttpJsonResponse(ResponseObject('error', 'Mismatch Token !!!', 401))
            
			return func(request, *args, **kwargs)
        
		wrapper.__doc__ = func.__doc__
		wrapper.__name__ = func.__name__
		return wrapper
    
	return decorator_wrapper


@csrf_exempt
@require_http_methods(['POST'])
def api_sign_up_with_email(request):
	return web.sign_up_with_email(request)


@csrf_exempt
@require_http_methods(['POST'])
def api_sign_up_with_google(request):
	return web.sign_up_with_google(request)


@csrf_exempt
@require_http_methods(['POST'])
def api_login(request):
	return web.login(request)


@csrf_exempt
def api_submit_reset_password(request):
	return web.submit_reset_password(request)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_user_profile_image(request):
	return web.update_user_profile_image(request)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_user_email(request):
	return web.update_user_email(request)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_user_password(request):
	return web.update_user_password(request)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_user_identity(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
        
		phone = request.POST.get('phone')
		dob = request.POST.get('date_of_birth')

		user.phone = phone if phone != None or phone != '' else  ''

		if dob != None or dob != '':
			try:
				date = datetime.strptime(dob, '%Y-%m-%d')
			except ValueError:
				return HttpJsonResponse(ResponseObject('error', 'Insert Valid Date Of Birth !!!', 406))

		name = request.POST.get('name')
		username = request.POST.get('username')
		gender = request.POST.get('gender')

		if username != user.username:
			check_username = User.objects.filter(username=username).count()
			if check_username == 0:
				user.username = username
			else:
				return HttpJsonResponse(ResponseObject('error', 'Username Is Already Taken !!!', 406))


		user.name = name
		user.gender = gender
		user.date_of_birth = dob if dob != None or dob != '' else ''
		user.updated_at = timezone.now()
		user.save()

		return HttpJsonResponse(ResponseObject('success', 'User Info Updated Successfully !!!', 200, user=user.to_json))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@csrf_exempt
@authenticate_user(xhr='api')
def api_add_user_address(request):
	return web.add_user_address(request)


@csrf_exempt
@authenticate_user(xhr='api')
def api_delete_user_address(request, address):
	return web.delete_user_address(request, address)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_user_address(request, address):
	return web.update_user_address(request, address)


def api_user_get(request, user):
	usr = User.objects.get(pk=user)
	return HttpResponse(json.dumps(usr.to_json_u, default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_user_get_auth(request):
	user = User.objects.get(pk=request.session['user'])
	return HttpResponse(json.dumps(user.to_json_u, default=str), content_type='application/json')


def api_user_map_pin(request, user):
	user = User.objects.get(pk=user)
	return HttpResponse(json.dumps({
			'id': user.pk,
			'pin': user.get_pin_string
		}, default=str), content_type='application/json')



# RESTAURANT


@authenticate_user(xhr='api')
def api_restaurants(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	branches = Branch.objects.filter(country=country, town=town)
	
	page = request.GET.get('page', 1)
	paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)
	
	if paginator.num_pages >= int(page):
		try:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(1)], default=str)
		except EmptyPage:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(paginator.num_pages)], default=str)
	else:
		_branches = json.dumps([], default=str)

	return HttpResponse(_branches, content_type='application/json')


def api_restaurant_tables_location(request):
	branch_id = request.GET.get('branch')
	try:
		branch = Branch.objects.get(pk=branch_id)
		tables = {'locations': map(lambda t: {'id': t[0], 'name': t[1]}, utils.TABLE_LOCATION), 'tables': branch.available_table_location}
		return HttpResponse(json.dumps(tables, default=str), content_type='application/json')
	except Branch.DoesNotExist:
		return HttpJsonResponse(ResponseObject('error', 'Branch Not Found', 404))


def api_restaurant_top_menus(request, branch):
	branch = Branch.objects.get(pk=branch)
	return HttpResponse(json.dumps([menu.to_json_s for menu in branch.menus.random(4)], default=str), content_type='application/json')


def api_get_restaurant(request, branch):
	branch = Branch.objects.get(pk=branch)
	return HttpResponse(json.dumps(branch.to_json_s, default=str), content_type='application/json')


def api_load_restaurant_promotions(request, branch):
	promotions = Promotion.objects.filter(branch__pk=branch).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(promotions, settings.PAGINATOR_ITEM_COUNT)

	if page != None:
		return HttpResponse(json.dumps([promotion.to_json for promotion in promotions], default=str), content_type='application/json')

	if paginator.num_pages >= int(page):
		try:
			_promotions = json.dumps([promotion.to_json for promotion in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_promotions = json.dumps([promotion.to_json for promotion in paginator.page(1)], default=str)
		except EmptyPage:
			_promotions = json.dumps([promotion.to_json for promotion in paginator.page(paginator.num_pages)], default=str)
	else:
		_promotions = json.dumps([], default=str)

	return HttpResponse(_promotions, content_type='application/json')


def api_promotion_promoted_menus(request, promo):
	promotion = Promotion.objects.get(pk=promo)
	promo_type = int(promotion.promotion_menu_type)

	if promo_type == 0:
		menus = Menu.objects.filter(branch__pk=promotion.branch.pk, restaurant__pk=promotion.restaurant.pk).random(4)
		return HttpResponse(json.dumps([menu.to_json_s for menu in menus], default=str), content_type='application/json')
	if promo_type in [1, 2, 3]:
		menus = Menu.objects.filter(branch__pk=promotion.branch.pk, restaurant__pk=promotion.restaurant.pk, menu_type=promo_type).random(4)
		return HttpResponse(json.dumps([menu.to_json_s for menu in menus], default=str), content_type='application/json')
	elif promo_type == 4:
		return HttpResponse(json.dumps([promotion.menu.to_json_s], default=str), content_type='application/json')
	elif promo_type == 5:
		foods = [food.menu for food in Food.objects.filter(branch__pk=promotion.branch.pk, restaurant__pk=promotion.restaurant.pk, category__pk=promotion.category.pk)]
		dishes = [dish.menu for dish in Dish.objects.filter(branch__pk=promotion.branch.pk, restaurant__pk=promotion.restaurant.pk, category__pk=promotion.category.pk)]
		menus = foods + dishes
		menu_itter = random.sample(menus, k=4) if len(menus) > 4 else menus
		return HttpResponse(json.dumps([menu.to_json_s for menu in menu_itter], default=str), content_type='application/json')
	else:
		return HttpResponse(json.dumps([], default=str), content_type='application/json')


def api_load_restaurant_foods(request, branch):
	foods = Menu.objects.filter(branch__pk=branch, menu_type=1).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(foods, settings.PAGINATOR_ITEM_COUNT)

	if page != None:
		return HttpResponse(json.dumps([food.to_json for food in foods], default=str), content_type='application/json')

	if paginator.num_pages >= int(page):
		try:
			_foods = json.dumps([food.to_json for food in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_foods = json.dumps([food.to_json for food in paginator.page(1)], default=str)
		finally:
			_foods = json.dumps([food.to_json for food in paginator.page(paginator.num_pages)], default=str)
	else:
		_foods = json.dumps([], default=str)

	return HttpResponse(_foods, content_type='application/json')


def api_load_restaurant_drinks(request, branch):
	drinks = Menu.objects.filter(branch__pk=branch, menu_type=2).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(drinks, settings.PAGINATOR_ITEM_COUNT)

	if page != None:
		return HttpResponse(json.dumps([drink.to_json for drink in drinks], default=str), content_type='application/json')

	if paginator.num_pages >= int(page):
		try:
			_drinks = json.dumps([drink.to_json for drink in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_drinks = json.dumps([drink.to_json for drink in paginator.page(1)], default=str)
		finally:
			_drinks = json.dumps([drink.to_json for drink in paginator.page(paginator.num_pages)], default=str)
	else:
		_drinks = json.dumps([], default=str)

	return HttpResponse(_drinks, content_type='application/json')


def api_load_restaurant_dishes(request, branch):
	dishes = Menu.objects.filter(branch__pk=branch, menu_type=3).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(dishes, settings.PAGINATOR_ITEM_COUNT)

	if page != None:
		return HttpResponse(json.dumps([dish.to_json for dish in dishes], default=str), content_type='application/json')

	if paginator.num_pages >= int(page):
		try:
			_dishes = json.dumps([dish.to_json for dish in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_dishes = json.dumps([dish.to_json for dish in paginator.page(1)], default=str)
		finally:
			_dishes = json.dumps([dish.to_json for dish in paginator.page(paginator.num_pages)], default=str)
	else:
		_dishes = json.dumps([], default=str)

	return HttpResponse(_dishes, content_type='application/json')


def api_load_restaurant_reviews(request, branch):
	reviews = RestaurantReview.objects.filter(branch__pk=branch).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(reviews, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_reviews = json.dumps([review.to_json_b for review in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_reviews = json.dumps([review.to_json_b for review in paginator.page(1)], default=str)
		finally:
			_reviews = json.dumps([review.to_json_b for review in paginator.page(paginator.num_pages)], default=str)
	else:
		_reviews = json.dumps([], default=str)

	return HttpResponse(_reviews, content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_like_restaurant(request, branch):
	b = Branch.objects.get(pk=branch)
	return web.like_restaurant(request, b.restaurant.pk, branch)


@csrf_exempt
@authenticate_user(xhr='api')
def api_add_restaurant_review(request, branch):
	b = Branch.objects.get(pk=branch)
	return web.add_restaurant_review(request, b.restaurant.pk, branch)


def api_load_restaurant_likes(request, branch):
	likes = UserRestaurant.objects.filter(branch__pk=branch).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(likes, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_likes = json.dumps([like.to_json for like in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_likes = json.dumps([like.to_json for like in paginator.page(1)], default=str)
		finally:
			_likes = json.dumps([like.to_json for like in paginator.page(paginator.num_pages)], default=str)
	else:
		_likes = json.dumps([], default=str)

	return HttpResponse(_likes, content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_check_restaurant_review(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		resto = request.POST.get('resto')
		review = RestaurantReview.objects.filter(branch__pk=resto, user__pk=user.pk).first()

		if review != None:
			return HttpResponse(json.dumps(review.to_json_b, default=str), content_type='application/json', status=200)
		else:
			return HttpResponse(json.dumps(ResponseObject('error', 'Review Not Found', 404), default=str), content_type='application/json', status=404)
	else:
		return HttpResponse(json.dumps(ResponseObject('error', 'Method Not Allowed', 405), default=str), content_type='application/json', status=404)


def api_restaurant_map_pin(request, branch):
	branch = Branch.objects.get(pk=branch)
	return HttpResponse(json.dumps({
			'id': branch.pk,
			'pin': branch.restaurant.get_pin_string
		}, default=str), content_type='application/json')


def api_get_restaurant_filters(request):
	filters = {
		'availability': utils.RESTAURANT_AVAILABILITY,
		'cuisines': map(lambda c: {'id': c.pk, 'title': c.name}, RestaurantCategory.objects.all()),
		'services': map(lambda s: {'id': s['id'], 'title': s['name']}, utils.RESTAURANT_SERVICES),
		'specials': map(lambda s: {'id': s['id'], 'title': s['name']}, utils.RESTAURANT_SPECIALS),
		'types': map(lambda t: {'id': t['id'], 'title': t['name']}, utils.RESTAURANT_TYPES),
		'ratings': utils.RESTAURANT_RATINGS
	}
	return HttpResponse(json.dumps(filters, default=str), content_type='application/json')


# To Review about search (user token request)
@csrf_exempt
@authenticate_user(xhr='api')
def api_filter_restaurants(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.POST.get('country') if request.POST.get('country') != None else user.country
	town = request.POST.get('town') if request.POST.get('town') != None else user.town
	query = request.POST.get('query')
	restaurants = Branch.objects.filter(country=country, town=town).filter(Q(restaurant__name__icontains=query) | Q(name__icontains=query))

	filters = json.loads(request.POST.get('filters'))

	brs__avail = map(lambda b: int(b.pk), list(filter(lambda b: b.availability in filters['availability'], restaurants)))
	brs__cuisines = map(lambda b: int(b.pk), list(filter(lambda b: any((True for c in filters['cuisines'] if c in list(map(lambda i: i.pk, b.restaurant.categories)))), restaurants)))
	brs__services = map(lambda b: int(b.pk), list(filter(lambda b: any((True for s in filters['services'] if s in map(lambda v: int(v), b.services_ids))), restaurants)))
	brs__specials = map(lambda b: int(b.pk), list(filter(lambda b: any((True for s in filters['specials'] if s in map(lambda v: int(v), b.specials_ids))), restaurants)))
	brs__types = map(lambda b: int(b.pk), list(filter(lambda b: b.restaurant_type in filters['types'], restaurants)))
	brs__ratings = map(lambda b: int(b.pk), list(filter(lambda b: b.review_average in filters['ratings'], restaurants)))

	brs__f__all = [brs__avail, brs__cuisines, brs__services, brs__specials, brs__types, brs__ratings]
	brs__k__all = [filters['availability'], filters['cuisines'], filters['services'], filters['specials'], filters['types'], filters['ratings']]
	
	brs__ids__pts = [brs[0] for brs in zip(*[bs for i, bs in enumerate(brs__f__all) if len(brs__k__all[i]) != 0]) if len(set(brs)) == 1]
	brs__ids__all = brs__ids__pts if len(list(filter(lambda b: len(b) != 0, brs__f__all))) != len(brs__f__all) else list(reduce(lambda x, y: x & y, (set(brs) for i, brs in enumerate(brs__f__all) if len(brs__k__all[i]) != 0)))

	branches = restaurants.filter(pk__in=brs__ids__all) if len(list(filter(lambda f: len(f) != 0, brs__k__all))) != 0 else restaurants
	
	page = request.POST.get('page', 1)
	paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)
	
	if paginator.num_pages >= int(page):
		try:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(1)], default=str)
		except EmptyPage:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(paginator.num_pages)], default=str)
	else:
		_branches = json.dumps([], default=str)

	return HttpResponse(_branches, content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_make_reservation(request):
	branch_id = request.POST.get('branch')
	try:
		branch = Branch.objects.get(pk=branch_id)
		return web.make_reservation(request, branch.restaurant.pk, branch.pk)
	except Branch.DoesNotExist:
		return HttpJsonResponse(ResponseObject('error', 'Branch Not Found', 404))


# MENU


def api_get_menu(request, menu):
	menu = Menu.objects.get(pk=menu)
	return HttpResponse(json.dumps(menu.to_json_f_s, default=str), content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_like_menu(request, menu):
	return web.like_menu(request, menu)


def api_load_menu_reviews(request, menu):
	reviews = MenuReview.objects.filter(menu__pk=menu).order_by('-created_at')
	page = request.GET.get('page', 1)
	paginator = Paginator(reviews, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_reviews = json.dumps([review.to_json for review in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_reviews = json.dumps([review.to_json for review in paginator.page(1)], default=str)
		finally:
			_reviews = json.dumps([review.to_json for review in paginator.page(paginator.num_pages)], default=str)
	else:
		_reviews = json.dumps([], default=str)

	return HttpResponse(_reviews, content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_add_menu_review(request, menu):
	return web.add_menu_review(request, menu)


@csrf_exempt
@authenticate_user(xhr='api')
def api_check_menu_review(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		menu = request.POST.get('menu')
		review = MenuReview.objects.filter(menu__pk=menu, user__pk=user.pk).first()

		if review != None:
			return HttpResponse(json.dumps(review.to_json_s, default=str), content_type='application/json', status=200)
		else:
			return HttpResponse(json.dumps(ResponseObject('error', 'Review Not Found', 404), default=str), content_type='application/json', status=404)
	else:
		return HttpResponse(json.dumps(ResponseObject('error', 'Method Not Allowed', 405), default=str), content_type='application/json', status=405)


# PROMOTION


def api_get_promotion(request, promo):
	promotion = Promotion.objects.get(pk=promo)
	return HttpResponse(json.dumps(promotion.to_json_f_a, default=str), content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_interest_promotion(request, promo):
	return web.interest_promotion(request, promo)


# CUISINES


def api_get_cuisines(request):
	cuisines = RestaurantCategory.objects.all()
	return HttpResponse(json.dumps([cuisine.to_json for cuisine in cuisines], default=str), content_type='application/json', status=200)


def api_get_cuisine_restaurants(request, cuisine):
	cuisine = RestaurantCategory.objects.get(pk=cuisine)
	branches = sorted(set(cuisine.restaurants), key=lambda branch: branch.review_average, reverse=True)
	page = request.GET.get('page', 1)
	paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)
	
	if paginator.num_pages >= int(page):
		try:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(1)], default=str)
		except EmptyPage:
			_branches = json.dumps([branch.to_json_s for branch in paginator.page(paginator.num_pages)], default=str)
	else:
		_branches = json.dumps([], default=str)

	return HttpResponse(_branches, content_type='application/json')


def api_get_cuisine_menus(request, cuisine):
	cuisine = RestaurantCategory.objects.get(pk=cuisine)
	foods = [food.menu for food in Food.objects.filter(cuisine__pk=cuisine.pk)]
	dishes = [dish.menu for dish in Dish.objects.filter(cuisine__pk=cuisine.pk)]
	menus = sorted(set(foods + dishes), key=lambda menu: menu.to_json['menu']['reviews']['average'], reverse=True)

	page = request.GET.get('page', 1)
	paginator = Paginator(menus, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(1)], default=str)
		except EmptyPage:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(paginator.num_pages)], default=str)
	else:
		_menus = json.dumps([], default=str)

	return HttpResponse(_menus, content_type='application/json')


# DISCOVER


@authenticate_user(xhr='api')
def api_get_discover_restaurants(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	branches = Branch.objects.filter(country=country, town=town).order_by('-created_at')
	rand_branches = branches.random(5)
	return HttpResponse(json.dumps([branch.to_json_s for branch in rand_branches], default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_get_top_restaurants(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	branches = Branch.objects.filter(country=country, town=town).order_by('-created_at')[:20]
	top_branches = sorted(sorted(list(filter(lambda branch: branch.review_average >= 4, branches)), key=lambda branch: branch.reviews_count, reverse=True), key=lambda branch: branch.review_average, reverse=True)[:5]
	return HttpResponse(json.dumps([branch.to_json_s for branch in top_branches], default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_get_today_promotions_rand(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	promotions = Promotion.objects.filter(branch__country=country, branch__town=town, is_on=True)[:20]
	today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))[:10]

	for i in range(4, len(today_promos)):
		today_promos.remove(random.choice(today_promos))

	return HttpResponse(json.dumps([promo.to_json_s for promo in today_promos], default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_get_today_promotions_all(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	promotions = Promotion.objects.filter(branch__country=country, branch__town=town, is_on=True)
	today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))
	return HttpResponse(json.dumps([promo.to_json_s for promo in today_promos], default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_get_top_menus(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	menus_all = Menu.objects.filter(branch__country=country, branch__town=town)
	menus = sorted(sorted(list(filter(lambda menu: menu.review_average >= 4, menus_all)), key=lambda menu: menu.reviews_count, reverse=True), key=lambda menu: menu.review_average, reverse=True)[:5]
	return HttpResponse(json.dumps([menu.to_json_s for menu in menus], default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_get_discover_menus(request):
	user = User.objects.get(pk=request.session['user'])
	country = request.GET.get('country') if request.GET.get('country') != None else user.country
	town = request.GET.get('town') if request.GET.get('town') != None else user.town
	menus = Menu.objects.filter(branch__country=country, branch__town=town).random(5)
	return HttpResponse(json.dumps([menu.to_json_s for menu in menus], default=str), content_type='application/json')


# PLACEMENTS & ORDERS


@authenticate_user(xhr='api')
def api_request_table_restaurant(request):
	table_uuid = request.GET.get('table')
	table = RestaurantTable.objects.filter(uuid=table_uuid).first()
	user = User.objects.get(pk=request.session['user'])
	placement = Placement.objects.filter(table__uuid=table.uuid, user__pk=user.pk, is_done=False).first()
	
	if placement != None:
		return HttpResponse(json.dumps(placement.to_json, default=str), content_type='application/json')
	
	return HttpResponse(json.dumps(table.to_json, default=str), content_type='application/json') if table != None else HttpResponse(json.dumps(ResponseObject('error', 'Table Not Found', 404), default=str), content_type='application/json', status=404)


@authenticate_user(xhr='api')
def api_get_placement(request):
	token = request.GET.get('token')
	user = User.objects.get(pk=request.session['user'])
	placement = Placement.objects.filter(token=token).first()
	return HttpResponse(json.dumps(placement.to_json, default=str), content_type='application/json') if user.pk == placement.user.pk else HttpResponse(json.dumps(ResponseObject('info', 'You Are Not The Owner', 403), default=str), content_type='application/json', status=403)


@csrf_exempt
@authenticate_user(xhr='api')
def api_update_people_placement(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		placement_token = request.POST.get('token')
		people = request.POST.get('people')
		placement = Placement.objects.filter(token=placement_token).first()
		if placement.user.pk != user.pk:
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))
		placement.people = people
		placement.save()
		return HttpResponse(json.dumps(placement.to_json, default=str), content_type='application/json')
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@authenticate_user(xhr='api')
def api_get_restaurant_menu_orders(request):
	branch = request.GET.get('branch')
	menu_type = request.GET.get('type')
	query = request.GET.get('query')
	menus = Menu.objects.filter(branch__pk=branch, menu_type=menu_type, name__icontains=query)
	
	page = request.GET.get('page', 1)
	paginator = Paginator(menus, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(1)], default=str)
		except EmptyPage:
			_menus = json.dumps([menu.to_json_s for menu in paginator.page(paginator.num_pages)], default=str)
	else:
		_menus = json.dumps([], default=str)

	return HttpResponse(_menus, content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_place_order_menu(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		placement_token = request.POST.get('token')
		quantity = request.POST.get('quantity')
		conditions = request.POST.get('conditions')
		menu_id = request.POST.get('menu')
		menu = Menu.objects.get(pk=menu_id)

		if menu.menu_type == 1:
			food = Food.objects.get(pk=menu.menu_id)
			if food.is_available == False:
				return HttpJsonResponse(ResponseObject('error', 'Menu Not Available !!!', 202))
		elif menu.menu_type == 2:
			drink = Drink.objects.get(pk=menu.menu_id)
			if drink.is_available == False:
				return HttpJsonResponse(ResponseObject('error', 'Menu Not Available !!!', 202))
		elif menu.menu_type == 3:
			dish = Dish.objects.get(pk=menu.menu_id)
			if dish.is_available == False:
				return HttpJsonResponse(ResponseObject('error', 'Menu Not Available !!!', 202))

		placement = Placement.objects.filter(token=placement_token).first()

		if placement.user.pk != user.pk:
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

		if placement.bill == None:
			
			today = timezone.datetime.today()
			last_bill = Bill.objects.filter(branch__pk=placement.branch.pk, restaurant__pk=placement.restaurant.pk, created_at__date=today.date()).last()
			bill_number = int(last_bill.number) + 1 if last_bill != None else 1

			new_bill = Bill(
					restaurant=Restaurant.objects.get(pk=placement.restaurant.pk),
					branch=Branch.objects.get(pk=placement.branch.pk),
					number=utils.int_to_string(bill_number),
					token=get_random_string(200),
					placement_id=placement.pk,
					currency=placement.restaurant.config.currency
				)
			new_bill.save()

			placement.bill = Bill.objects.get(pk=new_bill.pk)
			placement.save()

		placement = Placement.objects.filter(token=placement_token).first()

		if placement.bill.is_complete:
			return HttpJsonResponse(ResponseObject('error', 'Bill Is Completed. Cannot Procceed With Order', 405))

		if menu.menu_type == 1:
			food = Food.objects.get(pk=menu.menu_id)
			order = Order(
				bill=Bill.objects.get(pk=placement.bill.pk),
				menu=Menu.objects.get(pk=menu.pk),
				token=get_random_string(200),
				quantity=quantity,
				price=utils.promoted_price(food.price, food.today_promotion_object),
				currency=food.currency,
				conditions=conditions,
				has_promotion=True if food.today_promotion_object != None else False,
				promotion=Promotion.objects.get(pk=food.today_promotion_object.pk) if food.today_promotion_object != None else None
			)
			order.save()
		elif menu.menu_type == 2:
			drink = Drink.objects.get(pk=menu.menu_id)
			order = Order(
				bill=Bill.objects.get(pk=placement.bill.pk),
				menu=Menu.objects.get(pk=menu.pk),
				token=get_random_string(200),
				quantity=quantity,
				price=utils.promoted_price(drink.price, drink.today_promotion_object),
				currency=drink.currency,
				conditions=conditions,
				has_promotion=True if drink.today_promotion_object != None else False,
				promotion=Promotion.objects.get(pk=drink.today_promotion_object.pk) if drink.today_promotion_object != None else None
			)
			order.save()
		elif menu.menu_type == 3:
			dish = Dish.objects.get(pk=menu.menu_id)
			order = Order(
				bill=Bill.objects.get(pk=placement.bill.pk),
				menu=Menu.objects.get(pk=menu.pk),
				token=get_random_string(200),
				quantity=quantity,
				price=utils.promoted_price(dish.price, dish.today_promotion_object),
				currency=dish.currency,
				conditions=conditions,
				has_promotion=True if dish.today_promotion_object != None else False,
				promotion=Promotion.objects.get(pk=dish.today_promotion_object.pk) if dish.today_promotion_object != None else None
			)
			order.save()

		notify_waiter_placed_order.now(placement.pk)

		return HttpJsonResponse(ResponseObject('success', 'Order Sent !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@csrf_exempt
@authenticate_user(xhr='api')
def api_re_place_order_menu(request, order):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		order = Order.objects.get(pk=order)
		placement = Placement.objects.get(pk=order.bill.placement_id)

		quantity = request.POST.get('quantity')
		conditions = request.POST.get('conditions')

		if placement.user.pk != user.pk:
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

		if order.menu.menu_type == 1:
			food = Food.objects.get(pk=order.menu.menu_id)
			price = utils.promoted_price(food.price, food.today_promotion_object)
		elif order.menu.menu_type == 2:
			drink = Drink.objects.get(pk=order.menu.menu_id)
			price = utils.promoted_price(drink.price, drink.today_promotion_object)
		elif order.menu.menu_type == 3:
			dish = Dish.objects.get(pk=order.menu.menu_id)
			price = utils.promoted_price(dish.price, dish.today_promotion_object)
		else:
			price = 0

		order.quantity = quantity
		order.conditions = conditions
		order.price = price
		order.is_declined = False
		order.is_delivered = False
		order.updated_at = timezone.now()
		order.save()

		notify_waiter_placed_order.now(placement.pk)

		return HttpJsonResponse(ResponseObject('success', 'Order Sent !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@csrf_exempt
@authenticate_user(xhr='api')
def api_cancel_order_menu(request, order):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		order = Order.objects.get(pk=order)
		placement = Placement.objects.get(pk=order.bill.placement_id)

		if placement.user.pk != user.pk: 
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))
		
		order.delete()
		notify_waiter_order_updated.now(placement.pk)

		return HttpJsonResponse(ResponseObject('success', 'Order Canceled !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@background(schedule=60)
def notify_waiter_placed_order(placement):
	placement = Placement.objects.get(pk=placement)
	branch_message = {
		'status': 200,
		'type': 'request_table_order',
		'uuid': pnconfig.uuid,
		'sender': placement.user.socket_data,
		'receiver': placement.branch.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
	}
	pubnub.publish().channel(placement.branch.channel).message(branch_message).pn_async(ting_publish_callback)

	if placement.waiter != None:
		waiter_message = {
			'status': 200,
			'type': 'request_w_table_order',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.waiter.socket_data,
			'message': None,
			'args': None,
			'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
		}
		pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)


@background(schedule=60)
def notify_waiter_order_updated(placement):
	placement = Placement.objects.get(pk=placement)
	branch_message = {
		'status': 200,
		'type': 'response_w_orders_updated',
		'uuid': pnconfig.uuid,
		'sender': placement.user.socket_data,
		'receiver': placement.branch.socket_data,
		'message': None,
		'args': None,
		'data': None
	}
	pubnub.publish().channel(placement.branch.channel).message(branch_message).pn_async(ting_publish_callback)

	if placement.waiter != None:
		waiter_message = {
			'status': 200,
			'type': 'response_w_orders_updated',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.waiter.socket_data,
			'message': None,
			'args': None,
			'data': None
		}
		pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)


@authenticate_user(xhr='api')
def api_get_placement_menu_orders(request):
	token = request.GET.get('token')
	query = request.GET.get('query')

	user = User.objects.get(pk=request.session['user'])
	placement = Placement.objects.filter(token=token).first()
	orders = Order.objects.filter(bill__pk=placement.bill.pk, menu__name__icontains=query) if placement.bill != None else []
	
	if placement.user.pk != user.pk: 
		return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

	page = request.GET.get('page', 1)
	paginator = Paginator(orders, settings.PAGINATOR_ITEM_COUNT)

	if paginator.num_pages >= int(page):
		try:
			_orders = json.dumps([order.to_json for order in paginator.page(page)], default=str)
		except PageNotAnInteger:
			_orders = json.dumps([order.to_json for order in paginator.page(1)], default=str)
		except EmptyPage:
			_orders = json.dumps([order.to_json for order in paginator.page(paginator.num_pages)], default=str)
	else:
		_orders = json.dumps([], default=str)

	return HttpResponse(_orders, content_type='application/json')


@authenticate_user(xhr='api')
def api_get_placement_bill(request):
	token = request.GET.get('token')
	placement = Placement.objects.filter(token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()

	if bill != None:

		orders = Order.objects.filter(bill__pk=bill.pk)
		extras = BillExtra.objects.filter(bill__pk=bill.pk)
		user = User.objects.get(pk=request.session['user'])

		if placement.user.pk != user.pk: 
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))
		
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

		return HttpResponse(json.dumps(bill.to_json, default=str), content_type='application/json')
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bill Not Found !!!', 404))

@csrf_exempt
@authenticate_user(xhr='api')
def api_placement_bill_update_tips(request):
	if request.method == 'POST':
		token = request.POST.get('token')
		tips = request.POST.get('tips')

		placement = Placement.objects.filter(token=token).first()
		bill = Bill.objects.filter(placement_id=placement.pk).first()

		user = User.objects.get(pk=request.session['user'])

		if placement.user.pk != user.pk: 
			return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

		if bill != None:

			extras_total = 0
			extras = BillExtra.objects.filter(bill__pk=bill.pk)

			for extra in extras:
				extras_total = extras_total + (extra.quantity * extra.price)

			if bill.is_paid or bill.is_requested: 
				return HttpJsonResponse(ResponseObject('error', 'Cannot Procceed. Bill Paid Or Requested !!!', 405))

			bill.tips = tips
			bill.extras_total = extras_total
			bill.total = bill.amount + extras_total + decimal.Decimal(tips) - ((bill.amount * bill.discount) / 100)
			bill.save()

			return HttpResponse(json.dumps(bill.to_json, default=str), content_type='application/json')
		else:
			return HttpJsonResponse(ResponseObject('error', 'Bill Not Found !!!', 404))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@authenticate_user(xhr='api')
def api_placement_bill_conplete(request):
	token = request.GET.get('token')
	placement = Placement.objects.filter(token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()

	user = User.objects.get(pk=request.session['user'])

	if placement.user.pk != user.pk: 
		return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

	if bill != None:

		extras_total = 0
		extras = BillExtra.objects.filter(bill__pk=bill.pk)

		for extra in extras:
			extras_total = extras_total + (extra.quantity * extra.price)

		bill.extras_total = extras_total
		bill.total = bill.amount + extras_total + bill.tips - ((bill.amount * bill.discount) / 100)
		bill.is_complete = True
		bill.save()

		return HttpResponse(json.dumps(bill.to_json, default=str), content_type='application/json')
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bill Not Found !!!', 404))


@authenticate_user(xhr='api')
def api_placement_bill_request(request):
	token = request.GET.get('token')
	placement = Placement.objects.filter(token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()

	user = User.objects.get(pk=request.session['user'])

	if placement.user.pk != user.pk: 
		return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

	if bill != None:

		extras_total = 0
		extras = BillExtra.objects.filter(bill__pk=bill.pk)

		for extra in extras:
			extras_total = extras_total + (extra.quantity * extra.price)

		bill.extras_total = extras_total
		bill.total = bill.amount + extras_total + bill.tips - ((bill.amount * bill.discount) / 100)
		bill.is_requested = True
		bill.is_complete = True
		bill.save()

		notify_waiter_bill_requested.now(placement.pk)

		return HttpResponse(json.dumps(bill.to_json, default=str), content_type='application/json')
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bill Not Found !!!', 404))


@authenticate_user(xhr='api')
def api_end_placement(request):
	token = request.GET.get('token')
	placement = Placement.objects.filter(token=token).first()
	bill = Bill.objects.filter(placement_id=placement.pk).first()

	user = User.objects.get(pk=request.session['user'])

	if placement.user.pk != user.pk: 
		return HttpJsonResponse(ResponseObject('error', 'Not The Owner !!!', 403))

	if placement.bill != None:
		
		if bill.is_complete and bill.is_paid:
			placement.is_done = True
			placement.save()
			
			notify_waiter_placement_terminated.now(placement.pk)
			return HttpJsonResponse(ResponseObject('success', 'Placement Terminated !!!', 200))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Bill Yet To Be Paid !!!', 200))
	else:
		notify_waiter_placement_terminated.now(placement.pk)
		return HttpJsonResponse(ResponseObject('success', 'Placement Terminated !!!', 200))


@background(schedule=60)
def notify_waiter_bill_requested(placement):
	placement = Placement.objects.get(pk=placement)
	branch_message = {
		'status': 200,
		'type': 'request_bill_request',
		'uuid': pnconfig.uuid,
		'sender': placement.user.socket_data,
		'receiver': placement.branch.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
	}
	pubnub.publish().channel(placement.branch.channel).message(branch_message).pn_async(ting_publish_callback)

	if placement.waiter != None:
		waiter_message = {
			'status': 200,
			'type': 'request_w_bill_request',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.waiter.socket_data,
			'message': None,
			'args': None,
			'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
		}
		pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)


@background(schedule=60)
def notify_waiter_placement_terminated(placement):
	placement = Placement.objects.get(pk=placement)
	branch_message = {
		'status': 200,
		'type': 'request_placement_terminated',
		'uuid': pnconfig.uuid,
		'sender': placement.user.socket_data,
		'receiver': placement.branch.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
	}
	pubnub.publish().channel(placement.branch.channel).message(branch_message).pn_async(ting_publish_callback)

	if placement.waiter != None:
		waiter_message = {
			'status': 200,
			'type': 'request_w_placement_terminated',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.waiter.socket_data,
			'message': None,
			'args': None,
			'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
		}
		pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)
	

@csrf_exempt
@authenticate_user(xhr='api')
def api_send_waiter_request(request):
	if request.method == 'POST':
		token = request.POST.get('token')
		placement = Placement.objects.filter(token=token).first()
		message_text = request.POST.get('message')

		message = PlacementMessage(
				placement=Placement.objects.get(pk=placement.pk),
				message=message_text
			)
		message.save()
		notify_waiter_request_message.now(placement.pk, message_text)
		return HttpJsonResponse(ResponseObject('success', 'Requested Sent Successfully !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@background(schedule=60)
def notify_waiter_request_message(placement, message):
	placement = Placement.objects.get(pk=placement)
	if placement.waiter != None:
		waiter_message = {
			'status': 200,
			'type': 'response_w_request_message',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.waiter.socket_data,
			'message': message,
			'args': None,
			'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
		}
		pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)
	else:
		branch_message = {
			'status': 200,
			'type': 'response_w_request_message',
			'uuid': pnconfig.uuid,
			'sender': placement.user.socket_data,
			'receiver': placement.branch.socket_data,
			'message': message,
			'args': None,
			'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
		}
		pubnub.publish().channel(placement.branch.channel).message(branch_message).pn_async(ting_publish_callback)


# MOMENT

@csrf_exempt
@authenticate_user(xhr='api')
@require_http_methods(['POST'])
def api_save_placement_moment(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		token = request.POST.get('token')
		placement = Placement.objects.filter(token=token).first()

		if placement != None:
			moment = Moment.objects.filter(placement__token=placement.token, user__pk=user.pk).first()
			if moment == None:
				moment =  Moment(
						user=User.objects.get(pk=user.pk),
						placement=Placement.objects.get(pk=placement.pk)
					)
				moment.save()

			media = MomentMediaForm(request.POST, request.FILES, instance=MomentMedia(
					moment=Moment.objects.get(pk=moment.pk)
				))

			if media.is_valid():
				media.save()	
				return HttpJsonResponse(ResponseObject('success', 'Moment Saved', 200))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Placement Not Found', 404))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# SEARCH


@require_http_methods(['GET'])
def api_live_search_response(request):
	query = request.GET.get('query')
	country = request.GET.get('country')
	town = request.GET.get('town')

	try:
		queries = query.split() if query != None else []
		queryset = reduce(operator.or_, [Q(name__icontains=q) for q in queries])
		branch_queryset = reduce(operator.or_, [Q(restaurant__name__icontains=q) | Q(name__icontains=q) for q in queries])

		branches = map(lambda branch: branch.json_search(queries), Branch.objects.filter(country=country, town=town).filter(branch_queryset).order_by('-created_at'))
		foods = map(lambda food: food.json_search(queries), Food.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))
		drinks = map(lambda drink: drink.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))
		dishes = map(lambda dish: dish.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))

		results = branches + foods + drinks + dishes
		response = sorted(results, key=lambda res: res['qp'], reverse=True)
		return HttpResponse(json.dumps(response[:20], default=str), content_type='application/json')
	except Exception:
		return HttpResponse(json.dumps([], default=str), content_type='application/json')


@require_http_methods(['GET'])
def api_menus_search_response(request):
	query = request.GET.get('query')
	country = request.GET.get('country')
	town = request.GET.get('town')

	try:
		queries = query.split() if query != None else []
		queryset = reduce(operator.or_, [Q(name__icontains=q) for q in queries])
	
		foods = map(lambda food: food.json_search(queries), Food.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))
		drinks = map(lambda drink: drink.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))
		dishes = map(lambda dish: dish.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at'))

		results = foods + drinks + dishes
		response = sorted(results, key=lambda res: res['qp'], reverse=True)

		page = request.GET.get('page', 1)
		paginator = Paginator(response, settings.PAGINATOR_ITEM_COUNT)

		if paginator.num_pages >= int(page):
			try:
				_menus = json.dumps([menu for menu in paginator.page(page)], default=str)
			except PageNotAnInteger:
				_menus = json.dumps([menu for menu in paginator.page(1)], default=str)
			except EmptyPage:
				_menus = json.dumps([menu for menu in paginator.page(paginator.num_pages)], default=str)
		else:
			_menus = json.dumps([], default=str)

		return HttpResponse(_menus, content_type='application/json')
	except Exception:
		return HttpResponse(json.dumps([], default=str), content_type='application/json')


@require_http_methods(['GET'])
def api_restaurants_search_response(request):
	query = request.GET.get('query')
	country = request.GET.get('country')
	town = request.GET.get('town')

	try:
		queries = query.split() if query != None else []
		branch_queryset = reduce(operator.or_, [Q(restaurant__name__icontains=q) | Q(name__icontains=q) for q in queries])
		branches = map(lambda branch: branch.json_search(queries), Branch.objects.filter(country=country, town=town).filter(branch_queryset).order_by('-created_at'))

		response = sorted(branches, key=lambda res: res['qp'], reverse=True)

		page = request.GET.get('page', 1)
		paginator = Paginator(response, settings.PAGINATOR_ITEM_COUNT)
		
		if paginator.num_pages >= int(page):
			try:
				_branches = json.dumps([branch for branch in paginator.page(page)], default=str)
			except PageNotAnInteger:
				_branches = json.dumps([branch for branch in paginator.page(1)], default=str)
			except EmptyPage:
				_branches = json.dumps([branch for branch in paginator.page(paginator.num_pages)], default=str)
		else:
			_branches = json.dumps([], default=str)

		return HttpResponse(_branches, content_type='application/json')
	except Exception:
		return HttpResponse(json.dumps([], default=str), content_type='application/json')