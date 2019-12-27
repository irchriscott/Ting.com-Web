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
from django.core import serializers
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.backend import UserAuthentication
from tingweb.mailer import SendUserResetPasswordMail, SendUserUpdateEmailMail, SendUserSuccessResetPasswordMail
from tingweb.models import (
                                Restaurant, User, UserResetPassword, UserAddress, Branch, UserRestaurant, Menu,
                                MenuLike, MenuReview, Promotion, PromotionInterest, RestaurantReview, Booking
                            )
from tingweb.forms import (
                                GoogleSignUpForm, UserLocationForm, EmailSignUpForm, UserImageForm, MenuReviewForm,
                                RestaurantReviewForm, ReservationForm
                            )
import tingweb.views as web
import ting.utils as utils
from datetime import datetime, timedelta
import json
import imgkit
import os
import re

# Create your views here.

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
def api_sign_up_with_email(request):
	return web.sign_up_with_email(request)


@csrf_exempt
def api_sign_up_with_google(request):
	return web.sign_up_with_google(request)


@csrf_exempt
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

		return HttpJsonResponse(ResponseObject('success', 'User Info Updated Successfully !!!', 200, user=user.to_json()))
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
	return HttpResponse(json.dumps(usr.to_json_u(), default=str), content_type='application/json')


@authenticate_user(xhr='api')
def api_user_get_auth(request):
	user = User.objects.get(pk=request.session['user'])
	return HttpResponse(json.dumps(user.to_json_u(), default=str), content_type='application/json')


# RESTAURANT


def api_restaurants(request):
	branches = json.dumps([branch.to_json_r() for branch in Branch.objects.all()], default=str)
	return HttpResponse(branches, content_type='application/json')


def api_get_restaurant(request, branch):
	branch = Branch.objects.get(pk=branch)
	return HttpResponse(json.dumps(branch.to_json(), default=str), content_type='application/json')


def api_load_restaurant_promotions(request, branch):
	promotions = Promotion.objects.filter(branch__pk=branch).order_by('-created_at')
	return HttpResponse(json.dumps([promotion.to_json_f() for promotion in promotions], default=str), content_type='application/json')


def api_load_restaurant_foods(request, branch):
	foods = Menu.objects.filter(branch__pk=branch, menu_type=1).order_by('-created_at')
	return HttpResponse(json.dumps([food.to_json() for food in foods], default=str), content_type='application/json')


def api_load_restaurant_drinks(request, branch):
	drinks = Menu.objects.filter(branch__pk=branch, menu_type=2).order_by('-created_at')
	return HttpResponse(json.dumps([drink.to_json() for drink in drinks], default=str), content_type='application/json')


def api_load_restaurant_dishes(request, branch):
	dishes = Menu.objects.filter(branch__pk=branch, menu_type=3).order_by('-created_at')
	return HttpResponse(json.dumps([dish.to_json() for dish in dishes], default=str), content_type='application/json')


def api_load_restaurant_reviews(request, branch):
	reviews = RestaurantReview.objects.filter(branch__pk=branch).order_by('-created_at')
	return HttpResponse(json.dumps([review.to_json_b() for review in reviews], default=str), content_type='application/json')


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
	return HttpResponse(json.dumps([like.to_json() for like in likes], default=str), content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_check_restaurant_review(request):
	if request.method == 'POST':
		user = User.objects.get(pk=request.session['user'])
		resto = request.POST.get('resto')
		review = RestaurantReview.objects.filter(branch__pk=resto, user__pk=user.pk).first()

		if review != None:
			return HttpResponse(json.dumps(review.to_json_b(), default=str), content_type='application/json', status=200)
		else:
			return HttpResponse(json.dumps(ResponseObject('error', 'Review Not Found', 404), default=str), content_type='application/json', status=404)
	else:
		return HttpResponse(json.dumps(ResponseObject('error', 'Method Not Allowed', 405), default=str), content_type='application/json', status=404)


# MENU


def api_get_menu(request, menu):
	menu = Menu.objects.get(pk=menu)
	return HttpResponse(json.dumps(menu.to_json_f(), default=str), content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_like_menu(request, menu):
	return web.like_menu(request, menu)


def api_load_menu_reviews(request, menu):
	reviews = MenuReview.objects.filter(menu__pk=menu).order_by('-created_at')
	return HttpResponse(json.dumps([review.to_json() for review in reviews], default=str), content_type='application/json')


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
			return HttpResponse(json.dumps(review.to_json_s(), default=str), content_type='application/json', status=200)
		else:
			return HttpResponse(json.dumps(ResponseObject('error', 'Review Not Found', 404), default=str), content_type='application/json', status=404)
	else:
		return HttpResponse(json.dumps(ResponseObject('error', 'Method Not Allowed', 405), default=str), content_type='application/json', status=404)


# PROMOTION


def api_get_promotion(request, promo):
	promotion = Promotion.objects.get(pk=promo)
	return HttpResponse(json.dumps(promotion.to_json_f(), default=str), content_type='application/json')


@csrf_exempt
@authenticate_user(xhr='api')
def api_interest_promotion(request, promo):
	return web.interest_promotion(request, promo)