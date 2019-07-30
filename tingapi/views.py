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
