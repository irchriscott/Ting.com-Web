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
                                Placement, Order, Bill, BillExtra, PlacementMessage,
                            )
from tingadmin.models import RestaurantCategory
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from datetime import datetime, timedelta, date
from background_task import background
import tingweb.admin as admin
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
		if 'admin' not in request.session.keys():
			return HttpJsonResponse(ResponseObject('error', 'Login Required !!!', 401))
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
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=check_admin.to_json))
		else:
			check_admin.token = token
			check_admin.updated_at = timezone.now()
			check_admin.save()
			request.session['admin'] = check_admin.pk
                    
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=check_admin.to_json, msgs=[]))
	
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
			return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, link, user=auth.authenticate.to_json, msgs=[]))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Invalid Email or Password !!!', 404))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@csrf_exempt
def api_submit_reset_password(request):
	return admin.submit_reset_password(request)
