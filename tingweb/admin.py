# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.views.generic import TemplateView
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse, request
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.db.models.query import QuerySet
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.views.decorators.csrf import csrf_exempt
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.models import (
							Restaurant, Administrator, AdminPermission, RestaurantLicenceKey, RestaurantConfig,
							Menu, Food, Drink, Dish, FoodCategory, FoodImage, AdministratorResetPassword, DrinkImage,
							DishImage, DishFood, RestaurantTable, Branch, Promotion, User, Booking, UserNotification,
							CategoryRestaurant, Placement, Order, PlacementMessage, BillExtra, Bill, RestaurantReview
						)
from tingweb.backend import AdminAuthentication
from tingweb.mailer import (
							SendAdminRegistrationMail, SendAdminResetPasswordMail, SendAdminSuccessResetPasswordMail,
							SendAcceptedReservationMail, SendDeclinedReservationMail
							)
from tingweb.forms import (
							RestaurantUpdateLogo, RestaurantUpdateProfile, RestaurantUpdateConfig, 
							AdministratorUpdateImage, AdministratorUpdateProfile, AdministratorUpdateUsername, 
							AdministratorUpdateEmail, AddAdministrator, FoodCategoryForm, EditFoodCategoryForm,
							AddMenuFood, FoodImageForm, EditMenuFood, AddMenuDrink, DrinkImageForm, EditMenuDrink,
							AddMenuDish, DishImageForm, EditMenuDish, AddNewBranch, RestaurantTableForm, PromotionForm,
							PromotionEditForm, UpdateBranchProfile
						) 
from tingadmin.forms import RestaurantFormAdmin, BranchForm
from tingadmin.mailer import SendRestaurantRegistrationMail
from tingadmin.models import RestaurantCategory, TingPackage, TingLicenceKey
from pusher_push_notifications import PushNotifications
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from background_task import background
from tingweb.views import get_restaurant_map_pin_svg
from tingadmin import views as admin
from datetime import datetime, timedelta, date
import ting.utils as utils
import tingadmin.permissions as permissions
import operator
import pusher
import pytz
import json
import csv
import xlwt


pnconfig = PNConfiguration()
pnconfig.subscribe_key = utils.PUBNUB_SUBSCRIBE_KEY
pnconfig.publish_key = utils.PUBNUB_PUBLISH_KEY

pubnub = PubNub(pnconfig)

pusher_client = pusher.Pusher(
	app_id=utils.PUSHER_APP_ID,
	key=utils.PUSHER_KEY,
	secret=utils.PUSHER_SECRET,
	cluster=utils.PUSHER_CLUSTER,
	ssl=True
)

beams_client = PushNotifications(
    instance_id=utils.PUSHER_BEAMS_INSTANCE,
    secret_key=utils.PUSHER_BEAMS_SECRET_KEY,
)

# Login Decorators


def check_admin_login(func):
	def wrapper(request, *args, **kwargs):
		if 'admin' not in request.session.keys():
			messages.error(request, 'Login Required, Please !!!')
			return HttpResponseRedirect(reverse('ting_wb_adm_login'))
		return func(request, *args, **kwargs)
	wrapper.__doc__ = func.__doc__
	wrapper.__name__ = func.__name__
	return wrapper


def is_admin_enabled(func):
	def wrapper(request, *args, **kwargs):
		admin = Administrator.objects.get(pk=request.session['admin'])
		if admin.is_disabled == True:
			if request.method == 'POST' or request.is_ajax():
				return HttpJsonResponse(ResponseObject('error', 'Sorry, Your Account Has Been Disabled !!!', 401))
			else:
				messages.error(request, 'Sorry, Your Account Has Been Disabled !!!')
				return HttpResponseRedirect(reverse('ting_wb_adm_login'))
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
						if request.method == 'POST' or request.is_ajax():
							return HttpJsonResponse(ResponseObject('error', 'Permission Denied !!!', 401))
						else:
							messages.error(request, 'Permission Denied !!! !!!')
							return HttpResponseRedirect(reverse('ting_wb_adm_dashboard'))
				else:
					if admin.has_permission(permission) == False:
						if request.method == 'POST' or request.is_ajax():
							return HttpJsonResponse(ResponseObject('error', 'Permission Denied !!!', 401))
						else:
							messages.error(request, 'Permission Denied !!! !!!')
							return HttpResponseRedirect(reverse('ting_wb_adm_dashboard'))
	        
			return func(request, *args, **kwargs)
	    
		wrapper.__doc__ = func.__doc__
		wrapper.__name__ = func.__name__
		return wrapper
	
	return decorator_wrapper


# Pubnub Socket


def ting_publish_callback(envelope, status):
    pass


class TingSubscriptionCallback(SubscribeCallback):

	def status(self, pubnub, status):
		pass

	def presence(self, pubnub, presence):
		pass

	def message(self, pubnub, message):
		
		response = json.loads(str(message.message.replace("'", '"'))) if type(message.message) == str or type(message.message) == unicode else message.message

		if response['type'] == 'request_resto_table':
			
			user = response['sender']
			table = RestaurantTable.objects.filter(pk=response['args']['table']).first()
			
			if table != None:

				if table.is_available == True:
				
					token = response['args']['token']
					check_placement = Placement.objects.filter(token=token, user__pk=user['id'])

					send_pusher_notification(
						'New Client Placed', 
						'A new client has been placed on table %s' % table.number, 
						user['image'], '', 'placement', '', table.branch.channel)

					if check_placement.count() == 0:
						
						placement = Placement(
								restaurant=Restaurant.objects.get(pk=table.restaurant.pk),
								branch=Branch.objects.get(pk=table.branch.pk),
								user=User.objects.get(pk=int(user['id'])),
								table=RestaurantTable.objects.get(pk=table.pk),
								waiter=Administrator.objects.get(pk=table.waiter.pk) if table.waiter != None else None,
								token=token,
								people=1
							)
						placement.save()

						user_message = {
							'status': 200,
							'type': 'response_resto_table',
							'uuid': pnconfig.uuid,
							'sender': placement.branch.socket_data,
							'receiver': placement.user.socket_data,
							'message': None,
							'args': None,
							'data': {'token': placement.token}
						}

						pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)

						if table.waiter != None:
							
							if table.waiter.is_disabled == False:

								waiter_message = {
									'status': 200,
									'type': 'response_w_resto_table',
									'uuid': pnconfig.uuid,
									'sender': placement.branch.socket_data,
									'receiver': placement.waiter.socket_data,
									'message': None,
									'args': None,
									'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
								}

								pubnub.publish().channel(table.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)

								send_pusher_notification(
										'New Table For You', 
										'You have been assigned to the client on table %s' % placement.table.number, 
										placement.user.image.url, '', 'placement', placement.token, table.waiter.channel)

								try:
									pusher_client.trigger(placement.user.channel, placement.user.channel, {
											'title': 'Your Waiter', 
											'body': 'You will be served today by %s' % placement.waiter.name,
											'image': utils.HOST_END_POINT + placement.waiter.image.url,
											'navigate': 'current_restaurant',
											'data': placement.token
										})
								except Exception as e:
									pass
						
								try:
									beams_client.publish_to_interests(
								    	interests=[placement.user.channel],
								    	publish_body={
								        	'apns': {
								            	'aps': {
								                	'alert': {
									                	'title': 'Your Waiter',
									                	'body': 'You will be served today by %s' % placement.waiter.name
									            	}
								            	}
								        	},
								        	'fcm': {
								            	'notification': {
								                	'title': 'Your Waiter',
								                	'body': 'You will be served today by %s' % placement.waiter.name
								            	},
								            	'data': {
								            		'navigate': 'current_restaurant',
													'data': placement.token
								            	}
								        	}
								    	}
									)
								except Exception as e:
									pass
					else:
						
						placement = check_placement.first()

						if placement.is_done == False:

							user_message = {
								'status': 200,
								'type': 'response_resto_table',
								'uuid': pnconfig.uuid,
								'sender': placement.branch.socket_data,
								'receiver': placement.user.socket_data,
								'message': None,
								'args': None,
								'data': {'token': placement.token}
							}

							pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)
						else:

							user_message = {
								'status': 200,
								'type': 'response_resto_placement_done',
								'uuid': pnconfig.uuid,
								'sender': placement.branch.socket_data,
								'receiver': placement.user.socket_data,
								'message': None,
								'args': None,
								'data': None
							}

							pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)
				else:

					user_message = {
						'status': 404,
						'type': 'response_error',
						'uuid': pnconfig.uuid,
						'sender': None,
						'receiver': user,
						'message': 'Table Not Available',
						'args': None,
						'data': None
					}

					pubnub.publish().channel(user['channel']).message(user_message).pn_async(ting_publish_callback)

			else:
				user_message = {
					'status': 404,
					'type': 'response_error',
					'uuid': pnconfig.uuid,
					'sender': None,
					'receiver': user,
					'message': 'Table Not Found',
					'args': None,
					'data': None
				}

				pubnub.publish().channel(user['channel']).message(user_message).pn_async(ting_publish_callback)


def subscribe_ting_socket(func):
	def wrapper(request, *args, **kwargs):
		admin = Administrator.objects.get(pk=request.session['admin'])

		pubnub.add_listener(TingSubscriptionCallback())
		pubnub.subscribe().channels([admin.channel, admin.branch.channel]).with_presence().execute()
		
		return func(request, *args, **kwargs)
	
	wrapper.__doc__ = func.__doc__
	wrapper.__name__ = func.__name__
	return wrapper


# Login & Signup


def signup_restaurant(request):

	if request.method == 'POST':
		
		token = get_random_string(128)
		slug = '%s-%s' % (request.POST.get('name').replace(' ', '-').lower(), get_random_string(16))
		email = request.POST.get('email')
		phone = request.POST.get('phone')

		# Create Restaurant
		
		restaurant_form = RestaurantFormAdmin(request.POST, instance=Restaurant(
				token=token,
				slug=slug,
				logo=utils.DEFAULT_RESTAURANT_IMAGE
			))

		branch_form = BranchForm(request.POST, instance=Branch(
				name=request.POST.get('branch'),
				phone=phone,
				email=email,
				channel=get_random_string(64)
			))

		if restaurant_form.is_valid() and branch_form.is_valid():

			restaurant = restaurant_form.save()
			branch = branch_form.save(commit=False)
			branch.restaurant = Restaurant.objects.get(pk=restaurant.pk)
			branch.save()

			# Create Configuration For Restaurant

			config = RestaurantConfig(
					restaurant=get_object_or_404(Restaurant, pk=restaurant.pk),
					email=email,
					cancel_late_booking=30,
					phone=phone
				)

			config.save()

			# Default Administrator Account

			admin_token = get_random_string(128)
			password = get_random_string(8)

			admin = Administrator(
					restaurant=Restaurant.objects.get(pk=restaurant.pk),
					branch=Branch.objects.get(pk=branch.pk),
					token=admin_token,
					name=utils.DEFAULT_ADMIN_NAME,
					username=utils.DEFAULT_ADMIN_USERNAME,
					email=email,
					password=make_password(password),
					admin_type=utils.ADMIN_TYPE[0][0],
					channel=get_random_string(64),
					image=utils.DEFAULT_ADMIN_IMAGE,
					phone=phone
				)

			admin.save()

			# Administrator Permissions

			if restaurant.purpose == 1:

				_permissions = AdminPermission(
						admin=Administrator.objects.get(pk=admin.pk),
						permissions=','.join(permissions.admin_permissions)
					)

				_permissions.save()

			elif restaurant.purpose == 2:
				_permissions = AdminPermission(
						admin=Administrator.objects.get(pk=admin.pk),
						permissions=','.join(permissions.advertisment_account_permissions)
					)

				_permissions.save()
				

			# Create Trial Key

			key = TingLicenceKey(
					package=TingPackage.objects.get(pk=1),
					admin=User.objects.get(pk=request.session['ting']),
					key=get_random_string(20).upper(),
					duration=14,
					is_active=True
				)

			key.save()

			keyresto = RestaurantLicenceKey(
					restaurant=Restaurant.objects.get(pk=restaurant.pk),
					key=TingLicenceKey.objects.get(pk=key.pk),
					is_active=False
				)

			keyresto.save()

			# Send Mail

			message = SendRestaurantRegistrationMail(email=admin.email, context={
				'restaurant': restaurant.name, 
				'password': password, 
				'key': key.licence_key, 
				'email': admin.email
			})

			message.send()

			messages.success(request, 'Restaurant Registered Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Registered Successfully !!!', 200, 
                reverse('ting_wb_adm_login')))
		else:
			return HttpJsonResponse(
                ResponseObject('error', 'Fill All Fields With Rignt Data, Please !!!', 400, msgs=restaurant_form.errors.items() + branch_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


class AdminLogin(TemplateView):

	template = 'web/admin/login.html'

	def get(self, request, *args, **kwargs):
		if 'admin' in request.session.keys():
			return HttpResponseRedirect(reverse('ting_wb_adm_dashboard'))
		return render(request, self.template, {
				'is_logged_in': True if 'user' in request.session else False,
				'address_types': utils.USER_ADDRESS_TYPE,
				'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
				'types': utils.RESTAURANT_TYPES
			})

	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			email = request.POST.get('email')
			password = request.POST.get('password')

			auth = AdminAuthentication(email=email, password=password)

			if auth.authenticate != None:
				request.session['admin'] = auth.authenticate.pk
				
				messages.success(request, 'Administrator Logged In Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Administrator Logged In Successfully !!!', 200, 
                		reverse('ting_wb_adm_dashboard')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Invalid Email or Password !!!', 404))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def logout(request):
	try:
		del request.session['admin']
		messages.success(request, 'Admin Logged Out Successfully !!!')
		return HttpResponseRedirect(reverse('ting_wb_adm_login'))
	except KeyError:
		messages.error(request, 'No User Session Found !!!')
		return HttpResponseRedirect(reverse('ting_wb_adm_login'))


def submit_reset_password(request):
	if request.method == 'POST':
		email = request.POST.get('email')

		try:
			admin = Administrator.objects.get(email=email)
			reset = AdministratorResetPassword(
					admin=Administrator.objects.get(pk=admin.pk),
					email=email,
					token=get_random_string(32),
					expired_at=datetime.now() + timedelta(hours=24)
				)
			reset.save()

			mail = SendAdminResetPasswordMail(email=email, context={
					'name': admin.name,
					'link': reverse('ting_wb_adm_reset_pwd_link', kwargs={'token':reset.token})
				})
			mail.send()

			return HttpJsonResponse(ResponseObject('success', 'Reset Password Link Mail Sent Successfully !!!', 400))

		except Administrator.DoesNotExist as e:
			return HttpJsonResponse(ResponseObject('error', 'Unknown Administrator Email', 404))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def reset_password_link(request, token):
	try:
		reset = AdministratorResetPassword.objects.get(token=token)
		if reset.is_active == True:
			template = 'web/admin/reset_password.html'
			return render(request, template, {'token': token})
		else:
			messages.error(request, 'Link Has Expired !!!')
			return HttpResponseRedirect(reverse('ting_wb_adm_login'))
	except AdministratorResetPassword.DoesNotExist as e:
		messages.error(request, 'Invalid Token !!!!')
		return HttpResponseRedirect(reverse('ting_wb_adm_login'))


def reset_password(request, token):
	try:
		reset = AdministratorResetPassword.objects.get(token=token)
		link = reverse('ting_wb_adm_reset_pwd_link', kwargs={'token':token})
		if reset.is_active == True:
			if request.method == 'POST':
				password = request.POST.get('password')
				conf_password = request.POST.get('confirm_password')

				if password == conf_password:
					admin = Administrator.objects.get(pk=reset.admin.pk)
					admin.password = make_password(password)
					admin.updated_at = timezone.now()
					admin.save()

					reset.is_active = False
					reset.save()

					mail = SendAdminSuccessResetPasswordMail(email=admin.email, context={
							'name': admin.name,
							'link': reverse('ting_wb_adm_login'),
							'ip': request.POST.get('ip'),
							'location': request.POST.get('addr'),
							'time': timezone.now(),
							'tz': request.POST.get('tz'),
							'os': request.POST.get('os')
						})
					mail.send()

					messages.success(request, 'Password Updated Successfully !!!')
					return HttpResponseRedirect(reverse('ting_wb_adm_login'))
				else:
					messages.error(request, 'Passwords Didnt Match !!!')
					return HttpResponseRedirect(link)
			else:
				messages.error(request, 'Method Not Allowed !!!')
				return HttpResponseRedirect(link)
		else:
			messages.error(request, 'Link Has Expired !!!')
			return HttpResponseRedirect(reverse('ting_wb_adm_login'))
	except AdministratorResetPassword.DoesNotExist as e:
		messages.error(request, 'Invalid Token !!!!')
		return HttpResponseRedirect(reverse('ting_wb_adm_login'))


@check_admin_login
@is_admin_enabled
def welcome_to_ting(request):
	template = 'web/admin/welcome.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	key = RestaurantLicenceKey.objects.filter(restaurant=admin.restaurant.pk).last()

	if admin.restaurant.is_authenticated is True and key.is_active is True:
		return HttpResponseRedirect(reverse('ting_wb_adm_dashboard'))

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
def activate_licence_key(request):
	if request.method == 'POST':
		key = '{0}{1}{2}{3}{4}'.format(request.POST.get('key-1'), request.POST.get('key-2'), request.POST.get('key-3'), request.POST.get('key-4'), request.POST.get('key-5')).strip().upper()
		admin = Administrator.objects.get(pk=request.session['admin'])
		
		if len(key) is 20:
			check = RestaurantLicenceKey.objects.filter(restaurant=admin.restaurant.pk, key__key=key).first()
			if check is not None:
				if check.is_active is False:
					if check.key.is_active is True:
						restaurant = Restaurant.objects.get(pk=admin.restaurant.pk)
						restaurant.is_authenticated = True
						restaurant.save()

						check.is_active = True
						check.save()

						messages.success(request, 'The Restaurant Account Has Been Activated !!!')
						return HttpJsonResponse(ResponseObject('success', 'The Restaurant Account Has Been Activated !!!', 200,
								reverse('ting_wb_adm_dashboard')))
					else:
						return HttpJsonResponse(ResponseObject('error', 'This Licence Key Has Expired !!!', 403))
				else:
					return HttpJsonResponse(ResponseObject('info', 'You Have Already Activated This Key !!!', 403, 
							reverse('ting_wb_adm_dashboard')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Licence Key Not Found !!!', 404))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Key !!!', 406))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@subscribe_ting_socket
def dashboard(request):
	template = 'web/admin/dashboard.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	key = RestaurantLicenceKey.objects.filter(restaurant=admin.restaurant.pk).last()

	today = timezone.datetime.today()

	date_list = utils.get_dates_days(7)
	months_list = utils.get_dates_months(6)

	if admin.restaurant.is_authenticated is False:
		return HttpResponseRedirect(reverse('ting_wb_adm_welcome'))
	if key.is_active == False:
		return HttpResponseRedirect(reverse('ting_wb_adm_welcome'))

	managers_types = [1, 2, 5]

	placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=today) \
					if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
						Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=today, waiter__pk=admin.pk)

	today_bookings = Booking.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, date=today)
	bills = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=today, is_paid=True) \
				if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
					[bill for bill in Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=today, is_paid=True)
							if bill.placement.waiter != None and bill.placement.waiter.pk == admin.pk]
	
	reviews = RestaurantReview.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	waiters = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, admin_type=4)
	menus = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)

	total = 0
	for bill in bills: total += bill.total

	placements_data = []
	incomes_data = []
	waiters_data = []

	for date in date_list:
		placements_date = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date).count() \
							if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
								Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, waiter__pk=admin.pk).count()
		placements_data.append({'date': date.strftime('%d %b'), 'data': placements_date})
		
		bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True) \
				if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
					[bill for bill in Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
							if bill.placement.waiter != None and bill.placement.waiter.pk == admin.pk]

		incomes_data.append({'date': date.strftime('%d %b'), 'data': sum([bill.total for bill in bills_date])})

	for waiter in waiters:
		placements_waiter = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									waiter__pk=waiter.pk, created_at__date__in=date_list).count()

		placements_all = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									created_at__date__in=date_list).count()
			
		waiters_data.append({'date': waiter.name, 'data': (placements_waiter * 100) / placements_all if placements_all != 0 else 0})

	ordered_menus = Order.objects.filter(
						bill__branch__pk=admin.branch.pk, 
						bill__restaurant__pk=admin.restaurant.pk, 
						created_at__date__in=date_list).values('menu').annotate(orders=Count('menu')).order_by('-orders')[:8]

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str),
			'placements': len(placements),
			'bookings': len(today_bookings),
			'reviews': len(reviews),
			'incomes': total,
			'p__dt__charts': json.dumps(placements_data[::-1], default=str),
			'i__dt__charts': json.dumps(incomes_data[::-1], default=str),
			'w__dt__charts': json.dumps(waiters_data[::-1], default=str),
			'ordered_menus': ordered_menus
		})


@check_admin_login
@is_admin_enabled
def dashboard_data_charts(request):
	
	date_type = request.GET.get('type', 1)

	date_list = utils.get_dates_days(7)
	months_list = utils.get_dates_months(6)
	years_list = utils.get_dates_years(5)

	data = []
	managers_types = [1, 2, 5]

	placements_data = []
	incomes_data = []
	waiters_data = []

	admin = Administrator.objects.get(pk=request.session['admin'])
	waiters = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, admin_type=4)

	if int(date_type) == 1:
		for date in date_list:
			placements_date = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date).count() \
								if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
									Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, waiter__pk=admin.pk).count()
			placements_data.append({'date': date.strftime('%d %b'), 'data': placements_date})
			
			bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True) \
					if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
						[bill for bill in Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
								if bill.placement.waiter != None and bill.placement.waiter.pk == admin.pk]

			incomes_data.append({'date': date.strftime('%d %b'), 'data': sum([bill.total for bill in bills_date])})

		for waiter in waiters:
			placements_waiter = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									waiter__pk=waiter.pk, created_at__date__in=date_list).count()

			placements_all = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									created_at__date__in=date_list).count()
			
			waiters_data.append({'date': waiter.name, 'data': (placements_waiter * 100) / placements_all})

	elif int(date_type) == 2:
		for date in months_list:
			placements_date = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1]).count() \
								if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
									Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], waiter__pk=admin.pk).count()
			placements_data.append({'date': '%s %s' % (utils.get_month_name(date[1]), date[0]), 'data': placements_date})
			
			bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True) \
					if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
						[bill for bill in Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True)
								if bill.placement.waiter != None and bill.placement.waiter.pk == admin.pk]

			incomes_data.append({'date': '%s %s' % (utils.get_month_name(date[1]), date[0]), 'data': sum([bill.total for bill in bills_date])})
			
		for waiter in waiters:
			placements_waiter = Placement.objects.filter(branch__pk=admin.branch.pk, 
										restaurant__pk=admin.restaurant.pk, 
										waiter__pk=waiter.pk, created_at__year__in=list(map(lambda x: x[0], months_list)), 
										created_at__month__in=list(map(lambda x: x[1], months_list))).count()
				
			placements_all = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									created_at__year__in=list(map(lambda x: x[0], months_list)), 
									created_at__month__in=list(map(lambda x: x[1], months_list))).count()
			
			waiters_data.append({'date': waiter.name, 'data': (placements_waiter * 100) / placements_all})

	elif int(date_type) == 3:
		for date in years_list:
			placements_date = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date).count() \
								if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
									Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, waiter__pk=admin.pk).count()
			placements_data.append({'date': date, 'data': placements_date})
			
			bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, is_paid=True) \
					if int(admin.admin_type) in managers_types or admin.has_permission('can_view_incomes') else \
						[bill for bill in Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, is_paid=True)
								if bill.placement.waiter != None and bill.placement.waiter.pk == admin.pk]

			incomes_data.append({'date': date, 'data': sum([bill.total for bill in bills_date])})

		for waiter in waiters:
			placements_waiter = Placement.objects.filter(branch__pk=admin.branch.pk, 
										restaurant__pk=admin.restaurant.pk, 
										waiter__pk=waiter.pk, created_at__year__in=years_list).count()
				
			placements_all = Placement.objects.filter(branch__pk=admin.branch.pk, 
									restaurant__pk=admin.restaurant.pk, 
									created_at__year__in=years_list).count()
			
			waiters_data.append({'date': waiter.name, 'data': (placements_waiter) * 100 / placements_all})

	return HttpResponse(json.dumps([placements_data[::-1], incomes_data[::-1], waiters_data[::-1]], default=str), content_type='application/json')


@check_admin_login
@is_admin_enabled
def dashboard_menus_data(request):
	template = 'web/admin/ajax/load_dashboard_menus_data.html'
	date_type = request.GET.get('type', 1)

	admin = Administrator.objects.get(pk=request.session['admin'])

	date_list = utils.get_dates_days(7)
	months_list = utils.get_dates_months(6)
	years_list = utils.get_dates_years(5)

	managers_types = [1, 2, 5]

	if int(admin.admin_type) in managers_types:
		if int(date_type) == 1:
			menus = Order.objects.filter(
							bill__branch__pk=admin.branch.pk, 
							bill__restaurant__pk=admin.restaurant.pk, 
							created_at__date__in=date_list).values('menu').annotate(orders=Count('menu')).order_by('-orders')[:8]
		elif int(date_type) == 2:
			menus = Order.objects.filter(
							bill__branch__pk=admin.branch.pk, 
							bill__restaurant__pk=admin.restaurant.pk, 
							created_at__year__in=list(map(lambda x: x[0], months_list)),
							created_at__month__in=list(map(lambda x: x[1], months_list))).values('menu').annotate(orders=Count('menu')).order_by('-orders')[:8]
		elif int (date_type) == 3:
			menus = Order.objects.filter(
							bill__branch__pk=admin.branch.pk, 
							bill__restaurant__pk=admin.restaurant.pk, 
							created_at__year__in=years_list).values('menu').annotate(orders=Count('menu')).order_by('-orders')[:8]
		else:
			menus = QuerySet([])
	else:
		menus = QuerySet([])

	return render(request, template, {'menus': menus})


# Restaurant And Configurations


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
def restaurant(request):
	template = 'web/admin/restaurant.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	categories = RestaurantCategory.objects.all()
	currencies = utils.CURRENCIES
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'currencies': currencies,
			'specials': utils.RESTAURANT_SPECIALS,
			'branch': admin.branch,
			'modes': utils.BOOKING_PAYEMENT_MODE,
			'services': utils.RESTAURANT_SERVICES,
			'categories': categories,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant')
def update_restaurant_logo(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = RestaurantUpdateLogo(request.POST, request.FILES)

		if form.is_valid():
			restaurant = Restaurant.objects.get(pk=admin.restaurant.pk)
			restaurant.logo = form.cleaned_data['logo']
			restaurant.updated_at = timezone.now()
			restaurant.save()
			get_restaurant_map_pin_svg(request, restaurant.pk, True)
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Logo Updated Successfully !!!', 200))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Image !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant')
def update_restaurant_profile(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = RestaurantUpdateProfile(request.POST)
		
		email = request.POST.get('email')
		phone = request.POST.get('phone')
		password = request.POST.get('password')

		if form.is_valid() and email != '' and phone != '' and password != '':
			
			if check_password(password, admin.password) is True:
				
				slug = '%s-%s' % (form.cleaned_data['name'].replace(' ', '-').lower(), get_random_string(16))

				restaurant = Restaurant.objects.get(pk=admin.restaurant.pk)
				restaurant.name = form.cleaned_data['name']
				restaurant.slug = slug.lower()
				restaurant.motto = form.cleaned_data['motto']
				restaurant.opening = form.cleaned_data['opening']
				restaurant.closing = form.cleaned_data['closing']
				restaurant.updated_at = timezone.now()
				restaurant.save()

				config = RestaurantConfig.objects.get(restaurant=restaurant.pk)
				config.admin = Administrator.objects.get(pk=admin.pk)
				config.email = email
				config.phone = phone
				config.updated_at = timezone.now()
				config.save()

				messages.success(request, 'Restaurant Profile Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Restaurant Profile Updated Successfully !!!', 200, 
							reverse('ting_wb_adm_restaurant')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_configurations')
def update_restaurant_config(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = RestaurantUpdateConfig(request.POST)
		password = request.POST.get('password')

		if form.is_valid() and password != '':
			
			if check_password(password, admin.password) == True:

				config = RestaurantConfig.objects.get(restaurant=admin.restaurant.pk)
				config.admin = Administrator.objects.get(pk=admin.pk)
				config.currency = form.cleaned_data['currency']
				config.use_default_currency = form.cleaned_data['use_default_currency']
				config.tax = form.cleaned_data['tax']
				config.cancel_late_booking = form.cleaned_data['cancel_late_booking']
				config.waiter_see_all_orders = form.cleaned_data['waiter_see_all_orders']
				config.book_with_advance = form.cleaned_data['book_with_advance']
				config.booking_advance = form.cleaned_data['booking_advance']
				config.booking_cancelation_refund = form.cleaned_data['booking_cancelation_refund']
				config.booking_cancelation_refund_percent = form.cleaned_data['booking_cancelation_refund_percent']
				config.booking_payement_mode = form.cleaned_data['booking_payement_mode']
				config.days_before_reservation = form.cleaned_data['days_before_reservation']
				config.can_take_away = form.cleaned_data['can_take_away']
				config.user_should_pay_before = form.cleaned_data['user_should_pay_before']
				config.updated_at = timezone.now()
				config.save()

				messages.success(request, 'Restaurant Config Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Restaurant Config Updated Successfully !!!', 200, 
							reverse('ting_wb_adm_restaurant')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_branch')
def update_branch_profile(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = UpdateBranchProfile(request.POST)
		
		password = request.POST.get('password')
		specials = request.POST.getlist('specials')
		services = request.POST.getlist('services')

		if form.is_valid() and password != '':
			
			if check_password(password, admin.password) is True:
				
				branch = Branch.objects.get(pk=admin.branch.pk)
				branch.phone = form.cleaned_data['phone']
				branch.email = form.cleaned_data['email']
				branch.specials = ','.join(specials)
				branch.services = ','.join(services)
				branch.updated_at = timezone.now()
				branch.save()

				messages.success(request, 'Branch Profile Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Branch Profile Updated Successfully !!!', 200, 
							reverse('ting_wb_adm_restaurant')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_restaurant')
def update_restaurant_categories(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		restaurant = request.POST.get('restaurant')
		password = request.POST.get('password')

		categories = request.POST.getlist('categories')

		if check_password(password, admin.password) is True:
			
			CategoryRestaurant.objects.filter(restaurant__pk=admin.restaurant.pk).delete()
			
			for cat in categories:
				category = CategoryRestaurant(
						restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
						category=RestaurantCategory.objects.get(pk=cat)
					)
				category.save()

			messages.success(request, 'Restaurant Categories Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Categories Updated Successfully !!!', 200, 
							reverse('ting_wb_adm_restaurant')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# Branches


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_branch')
def branches(request):
	template = 'web/admin/branches.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk)
	types = utils.RESTAURANT_TYPES
	return render(request, template, {
			'branches': branches,
			'admin': admin,
			'restaurant': admin.restaurant,
			'types': types,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_branch', xhr='ajax')
def add_new_branch(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		branch = AddNewBranch(request.POST, instance=Branch(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					channel=get_random_string(64)
				))

		if branch.is_valid():
			branch.save()
			messages.success(request, 'Branch Created Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Branch Created Successfully', 200, 
						reverse('ting_wb_adm_branches')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=branch.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_branch', xhr='ajax')
def avail_branch_toggle(request, branch):
	admin = Administrator.objects.get(pk=request.session['admin'])
	branch = get_object_or_404(Branch, pk=branch)
	branch.updated_at = timezone.now()

	if admin.restaurant.pk != branch.restaurant.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_branches')))

	if branch.is_available == True:
		branch.is_available = False
		branch.save()

		messages.success(request, 'Branch Unavailed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Branch Unavailed Successfully !!!', 200, 
					reverse('ting_wb_adm_branches')))
	else:
		branch.is_available = True
		branch.save()

		messages.success(request, 'Branch Availed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Branch Availed Successfully !!!', 200, 
					reverse('ting_wb_adm_branches')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_branch', xhr='ajax')
def edit_branch(request, branch):
	template = 'web/admin/ajax/load_edit_branch.html'
	branch = Branch.objects.get(pk=branch)
	admin = Administrator.objects.get(pk=request.session['admin'])
	types = utils.RESTAURANT_TYPES
	return render(request, template, {
			'branch': branch,
			'admin': admin,
			'restaurant': admin.restaurant,
			'types': types
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_branch', xhr='ajax')
def update_branch(request, branch):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		branch = get_object_or_404(Branch, pk=branch)
		branch_form = AddNewBranch(request.POST)

		if admin.restaurant.pk != branch.restaurant.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_branches')))

		if branch_form.is_valid():
			branch.name = branch_form.cleaned_data['name']
			branch.address = branch_form.cleaned_data['address']
			branch.longitude = branch_form.cleaned_data['longitude']
			branch.latitude = branch_form.cleaned_data['latitude']
			branch.place_id = branch_form.cleaned_data['place_id']
			branch.region = branch_form.cleaned_data['region']
			branch.road = branch_form.cleaned_data['road']
			branch.email = branch_form.cleaned_data['email']
			branch.phone = branch_form.cleaned_data['phone']
			branch.updated_at = timezone.now()
			branch.save()
			
			messages.success(request, 'Branch Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Branch Updated Successfully', 200, 
						reverse('ting_wb_adm_branches')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=branch_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_branch', xhr='ajax')
def load_branch(request, branch):
	template = 'web/admin/ajax/load_branch.html'
	branch = Branch.objects.get(pk=branch)
	admin = Administrator.objects.get(pk=request.session['admin'])
	return render(request, template, {
			'branch': branch,
			'admin': admin,
			'restaurant': admin.restaurant
		})


# Administrators


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission=['can_view_admin', 'can_view_all_admin'])
def administrators(request):
	template = 'web/admin/administrators.html'	
	admin = Administrator.objects.get(pk=request.session['admin'])
	administrators = Administrator.objects.filter(restaurant__pk=admin.pk).order_by('name') if admin.has_permission('can_view_all_admin') else Administrator.objects.filter(restaurant__pk=admin.pk, branch__pk=admin.branch.pk).order_by('name')
	branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk)
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'administrators': administrators,
			'types': utils.ADMIN_TYPE,
			'branches': branches,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
def admin_session(request):
	template = 'web/admin/session.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	types = utils.ADMIN_TYPE
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'types': types,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_admin', xhr='ajax')
def load_admin_profile(request, token):
	template = 'web/admin/ajax/load_admin.html'
	admin = get_object_or_404(Administrator, token=token)
	return render(request, template, {'admin': admin})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_admin', xhr='ajax')
def add_new_admin(request):
	if request.method == 'POST':
		session = Administrator.objects.get(pk=request.session['admin'])

		admin_token = get_random_string(128)
		password = get_random_string(8)
		branch = int(request.POST.get('branch'))

		form = AddAdministrator(request.POST, instance=Administrator(
				restaurant=Restaurant.objects.get(pk=session.restaurant.pk),
				branch=Branch.objects.get(pk=branch),
				token=admin_token,
				image=utils.DEFAULT_ADMIN_IMAGE,
				channel=get_random_string(64),
				password=make_password(password)
			))

		if form.is_valid() and password != '':
			if check_password(request.POST.get('password'), session.password) == True:

				admin = form.save()

				if admin.restaurant.purpose == 1:
					_permissions = permissions.advertisment_new_account_permissions
				else:
					if admin.admin_type == 1:
						_permissions = permissions.admin_permissions
					elif admin.admin_type == 2:
						_permissions = permissions.supervisor_permissions
					elif admin.admin_type == 3:
						_permissions = permissions.chef_permissions
					elif admin.admin_type == 4:
						_permissions = permissions.waiter_permissions
					elif admin.admin_type == 5:
						_permissions = permissions.accountant_permission

				admin_permissions = AdminPermission(
						admin=Administrator.objects.get(pk=admin.pk),
						permissions=','.join(_permissions)
					)
				admin_permissions.save()

				mail = SendAdminRegistrationMail(email=admin.email, context={
						'admin': admin,
						'restaurant': admin.restaurant,
						'password': password,
						'branch': admin.branch
					})
				mail.send()

				messages.success(request, 'Administrator Created Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Administrator Created Successfully', 200, 
						reverse('ting_wb_adm_administrators')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_move_admin', xhr='ajax')
def move_admin_to_branch(request, token, branch):
	admin = Administrator.objects.get(token=token)
	branch = Branch.objects.get(pk=branch)
	session = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != session.restaurant.pk or branch.restaurant.pk != session.restaurant.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_administrators')))


	admin.branch = Branch.objects.get(pk=branch.pk)
	admin.updated_at = timezone.now()
	admin.save()

	messages.success(request, 'Admin Moved To %s Branch Successfully !!!' % branch.name)
	return HttpJsonResponse(ResponseObject('success', 'Admin Moved To %s Branch Successfully !!!' % branch.name, 200,
			reverse('ting_wb_adm_administrators')))


# Admin Profile


@check_admin_login
@is_admin_enabled
def update_admin_image(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = AdministratorUpdateImage(request.POST, request.FILES)

		if form.is_valid():
			admin.image = form.cleaned_data['image']
			admin.updated_at = timezone.now()
			admin.save()
			
			return HttpJsonResponse(ResponseObject('success', 'Admin Image Updated Successfully !!!', 200))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Image !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def edit_admin_profile(request, token):
	template = 'web/admin/ajax/load_edit_admin.html'
	admin = get_object_or_404(Administrator, token=token)
	return render(request, template, {'admin': admin, 'types': utils.ADMIN_TYPE})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def update_admin_profile(request, token):
	if request.method == 'POST':
		session = Administrator.objects.get(pk=request.session['admin'])
		form = AdministratorUpdateProfile(request.POST)
		password = request.POST.get('password')
		
		email = AdministratorUpdateEmail(request.POST)
		username = AdministratorUpdateUsername(request.POST)

		if form.is_valid() and password != '':
			if check_password(password, session.password) == True:

				admin = Administrator.objects.get(token=token)

				if admin.restaurant.pk != session.restaurant.pk:
					messages.error(request, 'Data Not For This Restaurant !!!')
					return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, reverse('ting_wb_adm_administrators')))

				if admin.username != request.POST.get('username'):
					if username.is_valid():
						admin.username = username.cleaned_data['username']
					else:
						return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=username.errors.items()))

				if admin.email != request.POST.get('email'):
					if email.is_valid():
						admin.email = email.cleaned_data['email']
					else:
						return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=email.errors.items()))
				
				admin.name = form.cleaned_data['name']
				admin.phone = form.cleaned_data['phone']
				admin.badge_number = form.cleaned_data['badge_number']
				admin.admin_type = form.cleaned_data['admin_type']
				admin.updated_at = timezone.now()
				admin.save()

				url = reverse('ting_wb_adm_admin_session') if admin.pk == session.pk else reverse('ting_wb_adm_administrators')

				messages.success(request, 'Administrator Profile Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Administrator Profile Updated Successfully !!!', 200, url))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_disable_admin', xhr='ajax')
def disable_admin_account_toggle(request, token):
	admin = Administrator.objects.get(token=token)
	session = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != session.restaurant.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_administrators')))

	if admin.pk != session.pk:
		if admin.is_disabled == False:
			admin.is_disabled = True
			admin.updated_at = timezone.now()
			admin.save()
		
			messages.success(request, 'Administrator Account Disabled !!!')
			return HttpJsonResponse(ResponseObject('success', 'Administrator Account Disabled !!!', 200, 
					reverse('ting_wb_adm_administrators')))
		elif admin.is_disabled == True:
			admin.is_disabled = False
			admin.updated_at = timezone.now()
			admin.save()
			messages.success(request, 'Administrator Account Enabled !!!')
			return HttpJsonResponse(ResponseObject('success', 'Administrator Account Enabled !!!', 200, 
					reverse('ting_wb_adm_administrators')))
	else:
		return HttpJsonResponse(ResponseObject('error', 'You Cannot Disable Your Self !!!', 400))


# Security


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
def admin_security(request):
	template = 'web/admin/security.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
def update_admin_password(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		oldpass = request.POST.get('oldpass')
		newpass = request.POST.get('newpass')
		confirmpass = request.POST.get('confirmpass')

		if check_password(oldpass, admin.password) == True:
			if newpass == confirmpass:
				admin.password = make_password(newpass)
				admin.updated_at = timezone.now()
				admin.save()

				messages.success(request, 'Password Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Password Updated Successfully !!!', 200, 
						reverse('ting_wb_adm_admin_security')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'New Passwords Dont Match !!!', 400))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Invalid Password !!!', 400))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# Permissions


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
def admin_permissions(request):
	template = 'web/admin/permissions.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	return render(request, template, {
			'admin': admin,
			'branch': permissions.branch,
			'restaurants': permissions.restaurant,
			'tables': permissions.tables,
			'administrators': permissions.administrators,
			'category': permissions.category,
			'menus': permissions.menus,
			'orders': permissions.orders,
			'bills': permissions.bills,
			'booking': permissions.booking,
			'management': permissions.management,
			'promotion': permissions.promotion,
			'placements': permissions.placements,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin')
def edit_admin_permissions(request, token):
	template = 'web/admin/ajax/load_permissions_admin.html'
	admin = Administrator.objects.get(token=token)
	return render(request, template, {
			'admin': admin,
			'branch': permissions.branch,
			'restaurants': permissions.restaurant,
			'tables': permissions.tables,
			'administrators': permissions.administrators,
			'category': permissions.category,
			'menus': permissions.menus,
			'orders': permissions.orders,
			'bills': permissions.bills,
			'booking': permissions.booking,
			'promotion': permissions.promotion,
			'management': permissions.management,
			'placements': permissions.placements,
			'restaurant': admin.restaurant
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin', xhr='ajax')
def update_admin_permissions(request, token):
	if request.method == 'POST':
		session = Administrator.objects.get(pk=request.session['admin'])
		admin = Administrator.objects.get(token=token)

		password = request.POST.get('password')
		_permissions = request.POST.getlist('permission')

		if admin.restaurant.pk != session.restaurant.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_administrators')))

		if check_password(password, session.password) == True:

			admin_permissions = AdminPermission.objects.get(admin=admin.pk)
			admin_permissions.permissions = ','.join(_permissions)
			admin_permissions.updated_at = timezone.now()

			admin_permissions.save()

			messages.success(request, 'Permissions Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Permissions Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_administrators')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Invalid Password !!!', 400))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# Categories


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_category')
def categories(request):
	template = 'web/admin/categories.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'categories': categories,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_category')
def add_new_category(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = FoodCategoryForm(request.POST, request.FILES, instance=FoodCategory(
				restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
				admin=Administrator.objects.get(pk=admin.pk),
				slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-'), get_random_string(32)).lower()
			))

		if form.is_valid():

			form.save()

			messages.success(request, 'Category Created Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Category Created Successfully !!!', 200, 
					reverse('ting_wb_adm_categories')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_category', xhr='ajax')
def delete_category(request, slug):
	admin = Administrator.objects.get(pk=request.session['admin'])
	category = FoodCategory.objects.get(slug=slug)

	if admin.restaurant.pk != category.restaurant.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_categories')))
	
	if category != None:
			
		# category.delete()

		messages.info(request, 'To Be Implemented Later !!!')
		return HttpJsonResponse(ResponseObject('info', 'To Be Implemented Later !!!', 200, 
				reverse('ting_wb_adm_categories')))
	else:
		return HttpJsonResponse(ResponseObject('error', 'You Cannot Disable Your Self !!!', 400))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_category', xhr='ajax')
def edit_category(request, slug):
	template = 'web/admin/ajax/load_edit_category.html'
	category = FoodCategory.objects.get(slug=slug)
	return render(request, template, {'category':category})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_category', xhr='ajax')
def update_category(request, slug):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = EditFoodCategoryForm(request.POST)
		category = FoodCategory.objects.get(slug=slug)
		
		if form.is_valid():

			if admin.restaurant.pk != category.restaurant.pk:
				messages.error(request, 'Data Not For This Restaurant !!!')
				return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
						reverse('ting_wb_adm_administrators')))
			
			category.name = form.cleaned_data['name']
			category.description = form.cleaned_data['description']

			if request.FILES.get('image') != None and request.FILES.get('image') != '':
				category.image = request.FILES.get('image')

			category.updated_at = timezone.now()
			category.save()

			messages.success(request, 'Category Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Category Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_categories')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# Menus Food


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_menu')
def menu_food(request):
	template = 'web/admin/menu_food.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	foods = Food.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	types = utils.FOOD_TYPE
	currencies = utils.CURRENCIES
	cuisines = CategoryRestaurant.objects.filter(restaurant__pk=admin.restaurant.pk)
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'foods': foods,
			'categories': categories,
			'types': types,
			'currencies': currencies,
			'cuisines': cuisines,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu', xhr='ajax')
def add_new_menu_food(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False
		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False

		branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk) if for_all_branches == True else Branch.objects.filter(pk=admin.branch.pk)

		for branch in branches:

			form = AddMenuFood(request.POST, instance=Food(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					branch=Branch.objects.get(pk=branch.pk),
					admin=Administrator.objects.get(pk=admin.pk),
					slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-').lower(), get_random_string(32)),
					category=FoodCategory.objects.get(pk=request.POST.get('category')),
					cuisine=RestaurantCategory.objects.get(pk=request.POST.get('cuisine')),
					is_countable=is_countable,
					show_ingredients=show_ingredients,
					quantity=int(request.POST.get('quantity')) if is_countable == True else 1
				))

			images_form = FoodImageForm(request.POST, request.FILES)

			if form.is_valid() and images_form.is_valid():

				food = form.save()
				images = request.FILES.getlist('image')

				for image in images:
					img = FoodImage(
							food=Food.objects.get(pk=food.pk),
							image=utils.compress_image(image, True)
						)
					img.save()

				menu = Menu(
						restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
						branch=Branch.objects.get(pk=branch.pk),
						admin=Administrator.objects.get(pk=admin.pk),
						name=food.name,
						menu_type=utils.MENU_TYPE[0][0],
						menu_id=food.pk,
						for_all_branches=for_all_branches
					)
				menu.save()

			messages.success(request, 'Menu Food Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Food Added Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu', xhr='ajax')
def avail_menu_food_toggle(request, food):
	food = get_object_or_404(Food, pk=food)
	food.admin = Administrator.objects.get(pk=request.session['admin'])
	food.updated_at = timezone.now()

	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	menu = Menu.objects.filter(menu_type=1, menu_id=food.pk).first()
	menu.admin = Administrator.objects.get(pk=request.session['admin'])
	menu.updated_at = timezone.now()
	menu.save()

	if food.is_available == True:
		food.is_available = False
		food.save()

		messages.success(request, 'Menu Food Unavailed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Food Unavailed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))
	else:
		food.is_available = True
		food.save()

		messages.success(request, 'Menu Food Availed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Food Availed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_food_to_type(request, food, food_type_key):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	food_type = utils.get_from_tuple(utils.FOOD_TYPE, food_type_key)

	if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	if food_type != None and food_type != food_type_key:
		food.food_type = int(food_type_key)
		food.admin = Administrator.objects.get(pk=admin.pk)
		food.updated_at = timezone.now()
		food.save()

		menu = Menu.objects.filter(menu_type=1, menu_id=food.pk).first()
		menu.admin = Administrator.objects.get(pk=admin.pk)
		menu.updated_at = timezone.now()
		menu.save()

		messages.success(request, 'Menu Food Type Changed To %s !!!' % food_type)
		return HttpJsonResponse(ResponseObject('success', 'Menu Food Type Changed To %s !!!' % food_type, 200, 
					reverse('ting_wb_adm_menu_food')))
	else:
		messages.error(request, 'Unknown Food Type !!!')
		return HttpJsonResponse(ResponseObject('error', 'Unknown Food Type !!!', 400, 
					reverse('ting_wb_adm_menu_food')))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_food_to_category(request, food, category):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	category = get_object_or_404(FoodCategory, pk=category)

	if admin.restaurant.pk != food.restaurant.pk or category.restaurant.pk != admin.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	food.category = FoodCategory.objects.get(pk=category.pk)
	food.admin = Administrator.objects.get(pk=admin.pk)
	food.updated_at = timezone.now()
	food.save()

	menu = Menu.objects.filter(menu_type=1, menu_id=food.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Menu Food Moved To Category %s !!!' % category.name)
	return HttpJsonResponse(ResponseObject('success', 'Menu Food Moved To Category %s !!!' % category.name, 200, 
					reverse('ting_wb_adm_menu_food')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_food_to_cuisine(request, food, category):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	category = get_object_or_404(RestaurantCategory, pk=category)

	if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	food.cuisine = RestaurantCategory.objects.get(pk=category.pk)
	food.admin = Administrator.objects.get(pk=admin.pk)
	food.updated_at = timezone.now()
	food.save()

	menu = Menu.objects.filter(menu_type=1, menu_id=food.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Menu Food Moved To Category %s !!!' % category.name)
	return HttpJsonResponse(ResponseObject('success', 'Menu Food Moved To Category %s !!!' % category.name, 200, 
					reverse('ting_wb_adm_menu_food')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def edit_menu_food(request, food):
	template = 'web/admin/ajax/load_edit_menu_food.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	
	return render(request, template, {
			'food':food, 
			'currencies':utils.CURRENCIES,
			'admin':admin, 
			'restaurant':admin.restaurant,
			'images': food.images
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def update_menu_food(request, food):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False

		food = get_object_or_404(Food, pk=food)
		form = EditMenuFood(request.POST)

		if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_menu_food')))

		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False
		foods = Food.objects.filter(name=food.name, restaurant__pk=food.restaurant.pk) if for_all_branches == True else Food.objects.filter(pk=food.pk)

		for foo in foods:

			if form.is_valid():

				foo.name = form.cleaned_data['name']
				foo.description = form.cleaned_data['description']
				foo.last_price = form.cleaned_data['last_price']
				foo.price = form.cleaned_data['price']
				foo.currency = form.cleaned_data['currency']
				foo.ingredients = form.cleaned_data['ingredients']
				foo.is_countable = is_countable
				foo.show_ingredients = show_ingredients
				foo.quantity = int(request.POST.get('quantity')) if is_countable == True else 1
				foo.admin = Administrator.objects.get(pk=admin.pk)
				foo.updated_at = timezone.now()

				foo.save()

				images = request.FILES.getlist('image')

				if len(images) > 0:
					for image in images:
						img = FoodImage(
								food=Food.objects.get(pk=foo.pk),
								image=utils.compress_image(image, True)
							)
						img.save()

				menu = Menu.objects.filter(menu_type=1, menu_id=foo.pk).first()
				menu.admin = Administrator.objects.get(pk=admin.pk)
				menu.name = foo.name
				menu.for_all_branches = for_all_branches
				menu.updated_at = timezone.now()
				menu.save()

			messages.success(request, 'Menu Food Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Food Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def delete_menu_food_image(request, food, image):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	image = get_object_or_404(FoodImage, pk=image)

	if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	if food.images.count() > 2:
		image.delete()
		return HttpJsonResponse(ResponseObject('success', 'Menu Food Image Deleted Successfully !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'The Menu Food Must Have More Than 2 Images To Perform This Action !!!', 400))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu', xhr='ajax')
def delete_menu_food(request, food):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)

	if admin.restaurant.pk != food.restaurant.pk or admin.branch.pk != food.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_food')))

	return HttpJsonResponse(ResponseObject('info', 'Action To Be Implemented Later !!!', 500))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu', xhr='ajax')
def load_menu_food(request, food):
	template = 'web/admin/ajax/load_menu_food.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	return render(request, template, {
			'food': food,
			'admin': admin,
			'restaurant': admin.restaurant
		})



# Menu Drinks


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_menu')
def menu_drinks(request):
	template = 'web/admin/menu_drinks.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	drinks = Drink.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'drinks': drinks,
			'currencies': utils.CURRENCIES,
			'types': utils.DRINK_TYPE,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu', xhr='ajax')
def add_new_menu_drink(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False
		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False

		branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk) if for_all_branches == True else Branch.objects.filter(pk=admin.branch.pk)

		for branch in branches:

			form = AddMenuDrink(request.POST, instance=Drink(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					branch=Branch.objects.get(pk=branch.pk),
					admin=Administrator.objects.get(pk=admin.pk),
					slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-').lower(), get_random_string(32)),
					is_countable=is_countable,
					show_ingredients=show_ingredients,
					quantity=int(request.POST.get('quantity')) if is_countable == True else 1
				))

			images_form = DrinkImageForm(request.POST, request.FILES)

			if form.is_valid() and images_form.is_valid():

				drink = form.save()
				images = request.FILES.getlist('image')

				for image in images:
					img = DrinkImage(
							drink=Drink.objects.get(pk=drink.pk),
							image=utils.compress_image(image, True)
						)
					img.save()

				menu = Menu(
						restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
						branch=Branch.objects.get(pk=branch.pk),
						admin=Administrator.objects.get(pk=admin.pk),
						name=drink.name,
						menu_type=utils.MENU_TYPE[1][0],
						menu_id=drink.pk,
						for_all_branches=for_all_branches
					)
				menu.save()

			messages.success(request, 'Menu Drink Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Drink Added Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_drinks')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu', xhr='ajax')
def avail_menu_drink_toggle(request, drink):
	drink = get_object_or_404(Drink, pk=drink)
	drink.admin = Administrator.objects.get(pk=request.session['admin'])
	drink.updated_at = timezone.now()

	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != drink.restaurant.pk or admin.branch.pk != drink.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_drinks')))

	menu = Menu.objects.filter(menu_type=2, menu_id=drink.pk).first()
	menu.admin = Administrator.objects.get(pk=request.session['admin'])
	menu.updated_at = timezone.now()
	menu.save()

	if drink.is_available == True:
		drink.is_available = False
		drink.save()

		messages.success(request, 'Menu Drink Unavailed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Drink Unavailed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_drinks')))
	else:
		drink.is_available = True
		drink.save()

		messages.success(request, 'Menu Drink Availed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Drink Availed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_drinks')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu', xhr='ajax')
def delete_menu_drink(request, drink):
	admin = Administrator.objects.get(pk=request.session['admin'])
	drink = get_object_or_404(Drink, pk=drink)

	if admin.restaurant.pk != drink.restaurant.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_drinks')))

	return HttpJsonResponse(ResponseObject('info', 'Action To Be Implemented Later !!!', 500))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_drink_to_type(request, drink, drink_type_key):
	admin = Administrator.objects.get(pk=request.session['admin'])
	drink = get_object_or_404(Drink, pk=drink)
	drink_type = utils.get_from_tuple(utils.DRINK_TYPE, drink_type_key)

	if admin.restaurant.pk != drink.restaurant.pk or admin.branch.pk != drink.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_drinks')))

	if drink_type != None and drink_type != drink_type_key:
		drink.drink_type = int(drink_type_key)
		drink.admin = Administrator.objects.get(pk=admin.pk)
		drink.updated_at = timezone.now()
		drink.save()

		menu = Menu.objects.filter(menu_type=2, menu_id=drink.pk).first()
		menu.admin = Administrator.objects.get(pk=admin.pk)
		menu.updated_at = timezone.now()
		menu.save()

		messages.success(request, 'Menu Drink Type Changed To %s !!!' % drink_type)
		return HttpJsonResponse(ResponseObject('success', 'Menu Drink Type Changed To %s !!!' % drink_type, 200, 
					reverse('ting_wb_adm_menu_drinks')))
	else:
		messages.error(request, 'Unknown Drink Type !!!')
		return HttpJsonResponse(ResponseObject('error', 'Unknown Drink Type !!!', 400, 
					reverse('ting_wb_adm_menu_drinks')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def edit_menu_drink(request, drink):
	template = 'web/admin/ajax/load_edit_menu_drink.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	drink = get_object_or_404(Drink, pk=drink)
	return render(request, template, {
			'drink':drink, 
			'currencies':utils.CURRENCIES,
			'admin':admin, 
			'restaurant':admin.restaurant,
			'images': drink.images
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def update_menu_drink(request, drink):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False

		drink = get_object_or_404(Drink, pk=drink)
		form = EditMenuDrink(request.POST)

		if admin.restaurant.pk != drink.restaurant.pk or admin.branch.pk != drink.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_menu_drinks')))

		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False
		drinks = Drink.objects.filter(name=drink.name, restaurant__pk=drink.restaurant.pk) if for_all_branches == True else Drink.objects.filter(pk=drink.pk)

		for drin in drinks:

			if form.is_valid():

				drin.name = form.cleaned_data['name']
				drin.description = form.cleaned_data['description']
				drin.last_price = form.cleaned_data['last_price']
				drin.price = form.cleaned_data['price']
				drin.currency = form.cleaned_data['currency']
				drin.ingredients = form.cleaned_data['ingredients']
				drin.is_countable = is_countable
				drin.show_ingredients = show_ingredients
				drin.quantity = int(request.POST.get('quantity')) if is_countable == True else 1
				drin.admin = Administrator.objects.get(pk=admin.pk)
				drin.updated_at = timezone.now()

				drin.save()

				images = request.FILES.getlist('image')

				if len(images) > 0:
					for image in images:
						img = DrinkImage(
								drink=Drink.objects.get(pk=drin.pk),
								image=utils.compress_image(image, True)
							)
						img.save()

				menu = Menu.objects.filter(menu_type=2, menu_id=drin.pk).first()
				menu.admin = Administrator.objects.get(pk=admin.pk)
				menu.name = drin.name
				menu.for_all_branches = for_all_branches
				menu.updated_at = timezone.now()
				menu.save()

			messages.success(request, 'Menu Drink Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Drink Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_drinks')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def delete_menu_drink_image(request, drink, image):
	admin = Administrator.objects.get(pk=request.session['admin'])
	drink = get_object_or_404(Drink, pk=drink)
	image = get_object_or_404(DrinkImage, pk=image)

	if admin.restaurant.pk != drink.restaurant.pk or admin.branch.pk != drink.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_drinks')))

	if drink.images.count() > 2:
		image.delete()
		return HttpJsonResponse(ResponseObject('success', 'Menu Drink Image Deleted Successfully !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'The Menu Drink Must Have More Than 2 Images To Perform This Action !!!', 400))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu', xhr='ajax')
def load_menu_drink(request, drink):
	template = 'web/admin/ajax/load_menu_drink.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	drink = get_object_or_404(Drink, pk=drink)
	
	return render(request, template, {
			'drink': drink,
			'admin': admin,
			'restaurant': admin.restaurant
		})


# Menus Dishes


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_menu')
def menu_dishes(request):
	template = 'web/admin/menu_dishes.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	dishes = Dish.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.restaurant.pk)
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	drinks = Drink.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk)
	cuisines = CategoryRestaurant.objects.filter(restaurant__pk=admin.restaurant.pk)
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'dishes': dishes,
			'categories': categories,
			'currencies': utils.CURRENCIES,
			'types': utils.DISH_TIME,
			'drinks': drinks,
			'cuisines': cuisines,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu', xhr='ajax')
def add_new_menu_dish(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False
		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False

		branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk) if for_all_branches == True else Branch.objects.filter(pk=admin.branch.pk)

		for branch in branches:

			form = AddMenuDish(request.POST, instance=Dish(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					branch=Branch.objects.get(pk=branch.pk),
					admin=Administrator.objects.get(pk=admin.pk),
					slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-').lower(), get_random_string(32)),
					category=FoodCategory.objects.get(pk=request.POST.get('category')),
					cuisine=RestaurantCategory.objects.get(pk=request.POST.get('cuisine')),
					is_countable=is_countable,
					show_ingredients=show_ingredients,
					quantity=int(request.POST.get('quantity')) if is_countable == True else 1
				))

			images_form = DishImageForm(request.POST, request.FILES)

			if form.is_valid() and images_form.is_valid():

				dish = form.save()
				images = request.FILES.getlist('image')

				for image in images:
					img = DishImage(
							dish=Dish.objects.get(pk=dish.pk),
							image=utils.compress_image(image, True)
						)
					img.save()

				menu = Menu(
						restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
						branch=Branch.objects.get(pk=branch.pk),
						admin=Administrator.objects.get(pk=admin.pk),
						name=dish.name,
						menu_type=utils.MENU_TYPE[2][0],
						menu_id=dish.pk,
						for_all_branches=for_all_branches
					)
				menu.save()

			messages.success(request, 'Menu Dish Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Dish Added Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu', xhr='ajax')
def avail_menu_dish_toggle(request, dish):
	dish = get_object_or_404(Dish, pk=dish)
	dish.admin = Administrator.objects.get(pk=request.session['admin'])
	dish.updated_at = timezone.now()

	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
	menu.admin = Administrator.objects.get(pk=request.session['admin'])
	menu.updated_at = timezone.now()
	menu.save()

	if dish.is_available == True:
		dish.is_available = False
		dish.save()

		messages.success(request, 'Menu Dish Unavailed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Dish Unavailed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))
	else:
		dish.is_available = True
		dish.save()

		messages.success(request, 'Menu Dish Availed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Dish Availed Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_dish_to_type(request, dish, dish_time_key):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	dish_time = utils.get_from_tuple(utils.DISH_TIME, dish_time_key)

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	if dish_time != None and dish_time != dish_time_key:
		dish.dish_time = int(dish_time_key)
		dish.admin = Administrator.objects.get(pk=admin.pk)
		dish.updated_at = timezone.now()
		dish.save()

		menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
		menu.admin = Administrator.objects.get(pk=admin.pk)
		menu.updated_at = timezone.now()
		menu.save()

		messages.success(request, 'Menu Dish Type Changed To %s !!!' % dish_time)
		return HttpJsonResponse(ResponseObject('success', 'Menu Dish Type Changed To %s !!!' % dish_time, 200, 
					reverse('ting_wb_adm_menu_dishes')))
	else:
		messages.error(request, 'Unknown Food Type !!!')
		return HttpJsonResponse(ResponseObject('error', 'Unknown Dish Type !!!', 400, 
					reverse('ting_wb_adm_menu_dishes')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_dish_to_category(request, dish, category):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	category = get_object_or_404(FoodCategory, pk=category)

	if admin.restaurant.pk != dish.restaurant.pk or category.restaurant.pk != admin.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	dish.category = FoodCategory.objects.get(pk=category.pk)
	dish.admin = Administrator.objects.get(pk=admin.pk)
	dish.updated_at = timezone.now()
	dish.save()

	menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Menu Dish Moved To Category %s !!!' % category.name)
	return HttpJsonResponse(ResponseObject('success', 'Menu Dish Moved To Category %s !!!' % category.name, 200, 
					reverse('ting_wb_adm_menu_dishes')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def move_menu_dish_to_cuisine(request, dish, category):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	category = get_object_or_404(RestaurantCategory, pk=category)

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	dish.cuisine = RestaurantCategory.objects.get(pk=category.pk)
	dish.admin = Administrator.objects.get(pk=admin.pk)
	dish.updated_at = timezone.now()
	dish.save()

	menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Menu Dish Moved To Category %s !!!' % category.name)
	return HttpJsonResponse(ResponseObject('success', 'Menu Dish Moved To Category %s !!!' % category.name, 200, 
					reverse('ting_wb_adm_menu_dishes')))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def edit_menu_dish(request, dish):
	template = 'web/admin/ajax/load_edit_menu_dish.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	
	return render(request, template, {
			'dish':dish, 
			'currencies':utils.CURRENCIES,
			'admin':admin, 
			'restaurant':admin.restaurant,
			'images': dish.images
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def update_menu_dish(request, dish):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') == 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') == 'on' else False

		dish = get_object_or_404(Dish, pk=dish)
		form = EditMenuDish(request.POST)

		if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_menu_dishes')))

		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False
		dishes = Dish.objects.filter(name=dish.name, restaurant__pk=dish.restaurant.pk) if for_all_branches == True else Dish.objects.filter(pk=dish.pk)

		for dis in dishes:

			if form.is_valid():

				dis.name = form.cleaned_data['name']
				dis.description = form.cleaned_data['description']
				dis.last_price = form.cleaned_data['last_price']
				dis.price = form.cleaned_data['price']
				dis.currency = form.cleaned_data['currency']
				dis.ingredients = form.cleaned_data['ingredients']
				dis.is_countable = is_countable
				dis.show_ingredients = show_ingredients
				dis.quantity = int(request.POST.get('quantity')) if is_countable == True else 1
				dis.admin = Administrator.objects.get(pk=admin.pk)
				dis.updated_at = timezone.now()

				dis.save()

				images = request.FILES.getlist('image')

				if len(images) > 0:
					for image in images:
						img = DishImage(
								dish=Dish.objects.get(pk=dis.pk),
								image=utils.compress_image(image, True)
							)
						img.save()

				menu = Menu.objects.filter(menu_type=3, menu_id=dis.pk).first()
				menu.admin = Administrator.objects.get(pk=admin.pk)
				menu.name = dis.name
				menu.for_all_branches = for_all_branches
				menu.updated_at = timezone.now()
				menu.save()

			messages.success(request, 'Menu Dish Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Dish Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def delete_menu_dish_image(request, dish, image):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	image = get_object_or_404(DishImage, pk=image)

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	if dish.images.count() > 2:
		image.delete()
		return HttpJsonResponse(ResponseObject('success', 'Menu Dish Image Deleted Successfully !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'The Menu Dish Must Have More Than 2 Images To Perform This Action !!!', 400))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_menu', xhr='ajax')
def delete_menu_dish(request, dish):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	return HttpJsonResponse(ResponseObject('info', 'Action To Be Implemented Later !!!', 500))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu', xhr='ajax')
def load_menu_dish(request, dish):
	template = 'web/admin/ajax/load_menu_dish.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	
	return render(request, template, {
			'dish': dish,
			'admin': admin,
			'restaurant': admin.restaurant
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def add_drink_to_menu_dish(request, dish, drink):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)
	drink = get_object_or_404(Drink, pk=drink)

	if admin.restaurant.pk != dish.restaurant.pk or drink.restaurant.pk != admin.restaurant.pk or admin.branch.pk != dish.branch.pk or admin.branch.pk != drink.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	dish.admin = Administrator.objects.get(pk=admin.pk)
	dish.has_drink = True
	dish.drink = Drink.objects.get(pk=drink.pk)
	dish.updated_at = timezone.now()
	dish.save()

	menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Drink Added To Menu Dish Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Drink Added To Menu Dish Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def remove_drink_to_menu_dish(request, dish):
	admin = Administrator.objects.get(pk=request.session['admin'])
	dish = get_object_or_404(Dish, pk=dish)

	if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_menu_dishes')))

	dish.admin = Administrator.objects.get(pk=request.session['admin'])
	dish.has_drink = False
	dish.drink = None
	dish.save()

	menu = Menu.objects.filter(menu_type=3, menu_id=dish.pk).first()
	menu.admin = Administrator.objects.get(pk=admin.pk)
	menu.updated_at = timezone.now()
	menu.save()

	messages.success(request, 'Drink Removed From Menu Dish Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Drink Removed From Menu Dish Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def load_menu_food_for_menu_dish(request, dish):
	template = 'web/admin/ajax/load_menu_food_for_menu_dish.html'
	dish = get_object_or_404(Dish, pk=dish)
	admin = Administrator.objects.get(pk=request.session['admin'])
	foods = Food.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk)
	
	return render(request, template, {
			'dish':dish,
			'foods': foods,
			'restaurant': admin.restaurant,
			'admin': admin
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def update_food_menu_for_dish_menu(request, dish):
	if request.method == 'POST':
		quantites = request.POST.getlist('quantity')
		foods = request.POST.getlist('food')
		dish = get_object_or_404(Dish, pk=dish)
		admin = Administrator.objects.get(pk=request.session['admin'])

		if admin.restaurant.pk != dish.restaurant.pk or admin.branch.pk != dish.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_menu_dishes')))

		DishFood.objects.filter(dish__pk=dish.pk).delete()
		
		if len(foods) > 0:
			for f in foods:
				data = f.split('-')
				food = Food.objects.get(pk=int(data[0]))
				
				if food.restaurant.pk == admin.restaurant.pk and admin.branch.pk == food.branch.pk:
					quantity = int(quantites[int(data[1]) - 1])
					new_df = DishFood(
								dish=Dish.objects.get(pk=dish.pk),
								food=Food.objects.get(pk=food.pk),
								quantity=quantity,
								is_countable=True if quantity != 1 else False
							)
					new_df.save()

		messages.success(request, 'Menu Dish Foods Updated Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Menu Dish Foods Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_dishes')))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


# Tables


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_table', xhr='ajax')
def tables(request):
	template = 'web/admin/tables.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	tables = RestaurantTable.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk)
	waiters = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, admin_type=4)

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'tables':tables,
			'locations': utils.TABLE_LOCATION,
			'types': utils.CHAIR_TYPE,
			'waiters': waiters,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_table', xhr='ajax')
def add_new_table(request):
	if request.method == 'POST':
			
		admin = Administrator.objects.get(pk=request.session['admin'])
		table = RestaurantTableForm(request.POST, instance=RestaurantTable(
				restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
				branch=Branch.objects.get(pk=admin.branch.pk),
				uuid=get_random_string(100).upper(),
				is_available=True
			))

		waiter = request.POST.get('waiter')

		if table.is_valid():

			table.save(commit=False)

			if waiter != None and waiter != "":
				table.waiter = Administrator.objects.get(pk=waiter)
			
			table.save()

			messages.success(request, 'Restaurant Table Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Table Added Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=table.errors.items()))

	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def load_edit_table(request, table):
	template = 'web/admin/ajax/load_edit_table.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	table = get_object_or_404(RestaurantTable, pk=table)
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'table':table,
			'locations': utils.TABLE_LOCATION,
			'types': utils.CHAIR_TYPE
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def update_table(request, table):
	if request.method == 'POST':
		
		admin = Administrator.objects.get(pk=request.session['admin'])
		table = get_object_or_404(RestaurantTable, pk=table)

		if admin.restaurant.pk != table.restaurant.pk or admin.branch.pk != table.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_tables')))

		form = RestaurantTableForm(request.POST)

		if form.is_valid():

			table.number = form.cleaned_data['number']
			table.location = form.cleaned_data['location']
			table.max_people = form.cleaned_data['max_people']
			table.chair_type = form.cleaned_data['chair_type']
			table.description = form.cleaned_data['description']
			table.updated_at = timezone.now()
			table.save()

			messages.success(request, 'Restaurant Table Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Table Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))

	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_table', xhr='ajax')
def avail_table_toggle(request, table):
	table = get_object_or_404(RestaurantTable, pk=table)
	table.updated_at = timezone.now()
	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != table.restaurant.pk or admin.branch.pk != table.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_tables')))

	if table.is_available == True:
		table.is_available = False
		table.save()

		messages.success(request, 'Restaurant Table Unavailed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Restaurant Unavailed Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))
	else:
		table.is_available = True
		table.save()

		messages.success(request, 'Restaurant Table Availed Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Restaurant Availed Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def assign_waiter_table(request, waiter, table):
	table = get_object_or_404(RestaurantTable, pk=table)
	table.updated_at = timezone.now()
	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != table.restaurant.pk or admin.branch.pk != table.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_tables')))

	table.waiter = Administrator.objects.get(pk=waiter)
	table.save()

	messages.success(request, 'Waiter Assigned To Table Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Waiter Assigned To Table Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_table', xhr='ajax')
def remove_waiter_table(request, table):
	table = get_object_or_404(RestaurantTable, pk=table)
	table.updated_at = timezone.now()
	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != table.restaurant.pk or admin.branch.pk != table.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_tables')))

	table.waiter = None
	table.save()

	messages.success(request, 'Waiter Remove To Table Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Waiter Removed To Table Successfully !!!', 200, 
					reverse('ting_wb_adm_tables')))


# Promotions


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_promotion')
def promotions(request):
	template = 'web/admin/promotions.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	promotions = Promotion.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	menus = Menu.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'promotions': promotions,
			'menus': menus,
			'promotion_types': utils.PROMOTION_MENU,
			'currencies': utils.CURRENCIES,
			'periods': utils.PROMOTION_PERIOD,
			'categories': categories,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_promotion', xhr='ajax')
def add_new_promotion(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False

		branches = Branch.objects.filter(restaurant__pk=admin.restaurant.pk) if for_all_branches == True else Branch.objects.filter(pk=admin.branch.pk)
		is_special = True if request.POST.get('is_special') == 'on' else False
		
		if is_special == True:
			try:
				sd = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
				ed = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
			except ValueError as e:
				return HttpJsonResponse(ResponseObject('error', 'Insert Valid Dates !!!', 406))

		periods = request.POST.get('promotion_period')
		start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d') if request.POST.get('start_date') != None and request.POST.get('start_date') != '' else ''
		end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d') if request.POST.get('end_date') != None and request.POST.get('end_date') != '' else ''

		if is_special == True:

			if request.POST.get('start_date') == '' or request.POST.get('start_date') == None or request.POST.get('end_date') == '' or request.POST.get('end_date') == None:
				return HttpJsonResponse(ResponseObject('error', 'Is Promotion Special Is Checked. Please, Enter Start Date And End Date !!!', 406))

			if start_date > end_date:
				return HttpJsonResponse(ResponseObject('error', 'Is Promotion Special Is Checked. Please, Enter Start Date Cannot Be Greater Than End Date !!!', 406))
		else:
			if periods == None or periods == '':
				return HttpJsonResponse(ResponseObject('error', 'Select Promotion Period !!!', 406))

		menu_type = request.POST.get('promotion_menu_type')
		selected_menu = request.POST.get('menu')
		selected_category = request.POST.get('category')

		if menu_type == '04' and (selected_menu == None or selected_menu == ''):
			return HttpJsonResponse(ResponseObject('error', 'You Have Selected Promotion Type To Be Specific Menu. Please, Enter That Specific Menu !!!', 406))

		if menu_type == '05' and (selected_category == None or selected_category == ''):
			return HttpJsonResponse(ResponseObject('error', 'You Have Selected Promotion Type To Be Specific Category. Please, Enter That Specific Category !!!', 406))

		has_reduction = True if request.POST.get('has_reduction') == 'on' else False
		amount = request.POST.get('amount')
		reduction_type = request.POST.get('reduction_type')

		if has_reduction == True and (amount == None or amount <= 0):
			return HttpJsonResponse(ResponseObject('error', 'Please, Enter The Reduction Amount Greater Than 0 !!!', 406))

		has_supplement = True if request.POST.get('has_supplement') == 'on' else False
		supplement_min_quantity = request.POST.get('supplement_min_quantity')
		is_supplement_same = True if request.POST.get('is_supplement_same') == 'on' else False
		supplement = request.POST.get('supplement')
		supplement_quantity = request.POST.get('supplement_quantity')

		if has_supplement == True and (supplement_min_quantity == None or supplement_min_quantity <= 0):
			return HttpJsonResponse(ResponseObject('error', 'Promotion Has Supplement Is Checked. Please Enter The Minimum Quantity For Supplement !!!', 406))
				
		if is_supplement_same == False and (supplement == None or supplement == ''):
			return HttpJsonResponse(ResponseObject('error', 'Is Supplement The Promoted Menu Is Not Checked. Please Select The Supplement Menu !!!', 406))

		if has_supplement == True and (supplement_quantity == None or supplement_quantity == ''):
			return HttpJsonResponse(ResponseObject('error', 'Promotion Has Supplement Is Checked. Please Enter The Quantity Of The Supplement !!!', 406))

		for branch in branches:

			form = PromotionForm(request.POST, request.FILES, instance=Promotion(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					admin=Administrator.objects.get(pk=admin.pk),
					branch=Branch.objects.get(pk=branch.pk),
					uuid=get_random_string(32),
					is_on=True
				))

			if form.is_valid():
				
				promotion = form.save(commit=False)

				promotion.menu = Menu.objects.get(pk=selected_menu) if menu_type == '04' else None
				promotion.category = FoodCategory.objects.get(pk=selected_category) if menu_type == '05' else None
				promotion.has_reduction = has_reduction
				promotion.amount = amount if has_reduction == True else 0
				promotion.reduction_type = reduction_type if has_reduction == True else None
				promotion.has_supplement = has_supplement
				promotion.supplement_min_quantity = supplement_min_quantity if has_supplement == True else 0
				promotion.is_supplement_same = is_supplement_same
				promotion.supplement = Menu.objects.get(pk=supplement) if is_supplement_same == False and has_supplement == True else None
				promotion.supplement_quantity = supplement_quantity if has_supplement == True else 0
				promotion.start_date = start_date if is_special == True else None
				promotion.end_date = end_date if is_special == True else None
				promotion.is_special = is_special
				promotion.promotion_period = periods if is_special == False else None
				promotion.for_all_branches = for_all_branches
				promotion.save()

			messages.success(request, 'Promotion Created Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Promotion Created Successfully !!!', 200, 
					reverse('ting_wb_adm_promotions')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))

	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_promotion', xhr='ajax')
def load_edit_promotion(request, promotion):
	template = 'web/admin/ajax/load_edit_promotion.html'
	promotion = Promotion.objects.get(pk=promotion)
	admin = Administrator.objects.get(pk=request.session['admin'])
	menus = Menu.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	categories = FoodCategory.objects.filter(restaurant__pk=admin.restaurant.pk)
	
	return render(request, template, {
			'promotion': promotion,
			'admin': admin,
			'restaurant': admin.restaurant,
			'menus': menus,
			'promotion_types': utils.PROMOTION_MENU,
			'currencies': utils.CURRENCIES,
			'periods': utils.PROMOTION_PERIOD,
			'categories': categories
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_promotion', xhr='ajax')
def update_promotion(request, promotion):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		form = PromotionEditForm(request.POST, request.FILES)
		promotion = Promotion.objects.get(pk=promotion)

		if admin.restaurant.pk != promotion.restaurant.pk or admin.branch.pk != promotion.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_promotions')))

		for_all_branches = True if request.POST.get('for_all_branches') == 'on' else False
		promotions = Promotion.objects.filter(occasion_event=promotion.occasion_event, restaurant__pk=promotion.restaurant.pk) if for_all_branches == True else Promotion.objects.filter(pk=promotion.pk)
		is_special = True if request.POST.get('is_special') == 'on' else False

		if is_special == True:
			try:
				sd = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
				ed = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
			except ValueError as e:
				return HttpJsonResponse(ResponseObject('error', 'Insert Valid Dates !!!', 406))

		if form.is_valid():

			periods = request.POST.get('promotion_period')
			start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d') if request.POST.get('start_date') != None and request.POST.get('start_date') != '' else ''
			end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d') if request.POST.get('end_date') != None and request.POST.get('end_date') != '' else ''

			if is_special == True:

				if request.POST.get('start_date') == '' or request.POST.get('start_date') == None or request.POST.get('end_date') == '' or request.POST.get('end_date') == None:
					return HttpJsonResponse(ResponseObject('error', 'Is Promotion Special Is Checked. Please, Enter Start Date And End Date !!!', 406))

				if start_date > end_date:
					return HttpJsonResponse(ResponseObject('error', 'Is Promotion Special Is Checked. Please, Enter Start Date Cannot Be Greater Than End Date !!!', 406))
			else:
				if periods == None or periods == '':
					return HttpJsonResponse(ResponseObject('error', 'Select Promotion Period !!!', 406))

			has_reduction = True if request.POST.get('has_reduction') == 'on' else False
			amount = request.POST.get('amount')
			reduction_type = request.POST.get('reduction_type')

			if has_reduction == True and (amount == None or amount <= 0):
				return HttpJsonResponse(ResponseObject('error', 'Please, Enter The Reduction Amount Greater Than 0 !!!', 406))

			has_supplement = True if request.POST.get('has_supplement') == 'on' else False
			supplement_min_quantity = request.POST.get('supplement_min_quantity')
			is_supplement_same = True if request.POST.get('is_supplement_same') == 'on' else False
			supplement = request.POST.get('supplement')
			supplement_quantity = request.POST.get('supplement_quantity')

			if has_supplement == True and (supplement_min_quantity == None or supplement_min_quantity <= 0):
				return HttpJsonResponse(ResponseObject('error', 'Promotion Has Supplement Is Checked. Please Enter The Minimum Quantity For Supplement !!!', 406))
			
			if is_supplement_same == False and (supplement == None or supplement == ''):
				return HttpJsonResponse(ResponseObject('error', 'Is Supplement The Promoted Menu Is Not Checked. Please Select The Supplement Menu !!!', 406))

			if has_supplement == True and (supplement_quantity == None or supplement_quantity == ''):
				return HttpJsonResponse(ResponseObject('error', 'Promotion Has Supplement Is Checked. Please Enter The Quantity Of The Supplement !!!', 406))

			for promo in promotions:

				if request.FILES.get('poster_image') != None and request.FILES.get('poster_image') != '':
					promo.poster_image = request.FILES.get('poster_image')
				
				promo.occasion_event = form.cleaned_data['occasion_event']
				promo.description = form.cleaned_data['description']
				promo.has_reduction = has_reduction
				promo.amount = amount if has_reduction == True else 0
				promo.reduction_type = reduction_type if has_reduction == True else None
				promo.has_supplement = has_supplement
				promo.supplement_min_quantity = supplement_min_quantity if has_supplement == True else 0
				promo.is_supplement_same = is_supplement_same
				promo.supplement = Menu.objects.get(pk=supplement) if is_supplement_same == False and has_supplement == True else None
				promo.supplement_quantity = supplement_quantity if has_supplement == True else 0
				promo.start_date = start_date if is_special == True else None
				promo.end_date = end_date if is_special == True else None
				promo.is_special = is_special
				promo.promotion_period = periods if is_special == False else None
				promo.updated_at = timezone.now()
				promo.save()

			messages.success(request, 'Promotion Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Promotion Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_promotions')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, msgs=form.errors.items()))

	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_promotion', xhr='ajax')
def avail_promotion_toggle(request, promotion):
	admin = Administrator.objects.get(pk=request.session['admin'])
	promotion = Promotion.objects.get(pk=promotion)

	if admin.restaurant.pk != promotion.restaurant.pk or admin.branch.pk != promotion.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_promotions')))

	if promotion.is_on == True:
		promotion.is_on = False
		promotion.updated_at = timezone.now()
		promotion.save()

		messages.success(request, 'Promotion Set To Off Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Promotion Set To Off Successfully !!!', 200, 
				reverse('ting_wb_adm_promotions')))
	elif promotion.is_on == False:
		promotion.is_on = True
		promotion.updated_at = timezone.now()
		promotion.save()

		messages.success(request, 'Promotion Set To On Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Promotion Set To On Successfully !!!', 200, 
					reverse('ting_wb_adm_promotions')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_promotion', xhr='ajax')
def delete_promotion(request, promotion):
	admin = Administrator.objects.get(pk=request.session['admin'])
	promotion = Promotion.objects.get(pk=promotion)

	if admin.restaurant.pk != promotion.restaurant.pk or admin.branch.pk != promotion.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_promotions')))

	messages.info(request, 'To Be Implemented Later !!!')
	return HttpJsonResponse(ResponseObject('info', 'To Be Implemented Later !!!', 200, 
			reverse('ting_wb_adm_promotions')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_promotion', xhr='ajax')
def load_promotion(request, promotion):
	template = 'web/admin/ajax/load_promotion.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	promotion = Promotion.objects.get(pk=promotion)

	if admin.restaurant.pk != promotion.restaurant.pk or admin.branch.pk != promotion.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_promotions')))

	return render(request, template, {
			'promotion': promotion,
			'admin': admin,
			'restaurant': admin.restaurant
		})


# Reservations


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_booking')
def reservations(request):
	template = 'web/admin/reservations.html'
	dt = date.today() if request.GET.get('date') == None else datetime.strptime(request.GET.get('date'), '%Y-%m-%d')
	admin = Administrator.objects.get(pk=request.session['admin'])
	today_bookings = Booking.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, date=dt).exclude(status=1).order_by('-updated_at')
	new_bookings = Booking.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, status=1).order_by('-updated_at')
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'bookings': today_bookings,
			'today': dt,
			'new_bookings': new_bookings,
			'admin_json': json.dumps(admin.to_json, default=str),
			'tables': RestaurantTable.objects.filter(restaurant__pk=admin.restaurant.pk, branch__pk=admin.branch.pk).order_by('-created_at')
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_booking')
def load_reservation(request, reservation):
	template = 'web/admin/ajax/load_reservation.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	booking = Booking.objects.get(pk=reservation)
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'booking': booking
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_accept_booking', 'can_cancel_booking'])
def accept_reservation(request, reservation):
	if request.method == 'POST':
		
		admin = Administrator.objects.get(pk=request.session['admin'])
		book = get_object_or_404(Booking, pk=reservation)

		if admin.restaurant.pk != book.restaurant.pk or admin.branch.pk != book.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_reservations')))

		table = RestaurantTable.objects.get(pk=request.POST.get('table'))
		if table.max_people < book.people:
			return HttpJsonResponse(ResponseObject('error', 'Table Has Few People Than Required !!!', 406))

		if table.restaurant.pk != admin.restaurant.pk or admin.branch.pk != table.branch.pk:
			messages.error(request, 'Table Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Table Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_reservations')))

		if book.status == 1:
			book.status = 3 if book.restaurant.config.book_with_advance == True else 4
			book.table = RestaurantTable.objects.get(pk=table.pk)
			book.updated_at = timezone.now()
			book.save()

			notif = UserNotification(
					user=User.objects.get(pk=book.user.pk),
					from_type=1,
					from_id=admin.branch.pk,
					message='has accepted your reservation of %s at %s.' % (str(book.date), str(book.time)) if admin.restaurant.config.book_with_advance == False else 'has accepted your reservation of %s at %s. Please, proceed with the payements.' % (str(book.date), str(book.time)),
					notif_type='book',
					url=reverse('ting_usr_bookings', kwargs={'user': book.user.pk, 'username': book.user.username})
				)
			notif.save()

			mail = SendAcceptedReservationMail(email=book.user.email, context={
					'name': book.user.name,
					'book': book,
					'link': reverse('ting_usr_bookings', kwargs={'user': book.user.pk, 'username': book.user.username})
				})
			mail.send()

			notify_user_booking_status.now(book.pk, True, '')
			messages.success(request, 'Reservation Accepted Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Reservation Accepted Successfully !!!', 200, 
					reverse('ting_wb_adm_reservations')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Cannot Accept This Reservation For Status Is %s !!!' % book.status_str, 406))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_accept_booking', 'can_cancel_booking'])
def decline_reservation(request, reservation):
	if request.method == 'POST':
		
		admin = Administrator.objects.get(pk=request.session['admin'])
		book = get_object_or_404(Booking, pk=reservation)

		if admin.restaurant.pk != book.restaurant.pk or admin.branch.pk != book.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_reservations')))

		if book.status == 1:
			book.status = 2
			book.updated_at = timezone.now()
			book.save()

			notif = UserNotification(
					user=User.objects.get(pk=book.user.pk),
					from_type=1,
					from_id=admin.branch.pk,
					message='has declined your reservation of %s at %s. Plase, Update your reservation' % (str(book.date), str(book.time)) ,
					notif_type='book',
					url=reverse('ting_usr_bookings', kwargs={'user': book.user.pk, 'username': book.user.username})
				)
			notif.save()

			mail = SendDeclinedReservationMail(email=book.user.email, context={
					'name': book.user.name,
					'book': book,
					'reasons': request.POST.get('reasons'),
					'link': reverse('ting_usr_bookings', kwargs={'user': book.user.pk, 'username': book.user.username})
				})
			mail.send()

			notify_user_booking_status.now(book.pk, False, request.POST.get('reasons'))
			messages.success(request, 'Reservation Declined Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Reservation Declined Successfully !!!', 200, 
					reverse('ting_wb_adm_reservations')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Cannot Accept This Reservation For It Is %s !!!' % book.status_str, 406))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@background(schedule=60)
def notify_user_booking_status(book, accepted, text):
	book = Booking.objects.get(pk=book)
	
	try:
		pusher_client.trigger(book.user.channel, book.user.channel, {
			'title': 'Reservation Accepted' if accepted == True else 'Reservation Declined', 
			'body': 'Your reservation of %s, %s at %s, %s has been %s.' % (book.date.strftime('%B %d, %Y'), book.time.strftime('%H:%I %p').upper(), book.restaurant.name, book.branch.name, "accepted" if accepted else "declined"),
			'image': utils.HOST_END_POINT + book.restaurant.logo.url,
			'text': text,
			'navigate': 'booking',
			'data': book.token
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[book.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Reservation Accepted' if accepted == True else 'Reservation Declined', 
							'body': 'Your reservation of %s, %s at %s, %s has been %s.' % (book.date, book.time, book.restaurant.name, book.branch.name, "accepted" if accepted else "declined"),
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Reservation Accepted' if accepted == True else 'Reservation Declined', 
						'body': 'Your reservation of %s, %s at %s, %s has been %s.' % (book.date, book.time, book.restaurant.name, book.branch.name, "accepted" if accepted else "declined"),
					},
					'data': {
						'navigate': 'booking',
						'data': book.token
					}
				}
			}
		)
	except Exception as e:
		pass


# PLACEMENTS & ORDERS


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_placements')
def placements(request):
	template = 'web/admin/placements.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	return render(request, template, {'admin': admin, 'restaurant': admin.restaurant, 'admin_json': json.dumps(admin.to_json, default=str)})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements')
def load_placements(request):
	template = 'web/admin/ajax/load_placements.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	if admin.admin_type == '4':
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, waiter=admin.pk, is_done=False).order_by('-created_at')
	else:
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, is_done=False).order_by('-created_at')
	waiters = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, admin_type=4, is_disabled=False)
	return render(request, template, {'placements': placements, 'waiters': waiters, 'admin': admin})


@check_admin_login
@is_admin_enabled
def load_placements_dashboard(request):
	template = 'web/admin/ajax/load_placements_dashboard.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	if admin.admin_type == '4':
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, waiter=admin.pk, is_done=False).order_by('-created_at')
	else:
		placements = Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, is_done=False).order_by('-created_at')
	
	return render(request, template, {'placements': placements, 'admin': admin})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements')
def load_user_placement(request, placement):
	template = 'web/admin/ajax/load_user_placement.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	placement = Placement.objects.get(pk=placement)
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
	
	else:
		
		orders = []
		extras = []

	if placement.branch.pk != admin.branch.pk:
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant ', 405))

	if placement.waiter != None:
		if placement.waiter.pk != admin.pk != None and admin.admin_type == '4':
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Admin ', 405))

	return render(request, template, {'admin': admin, 'placement': placement, 'orders': orders, 'extras': extras})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_placements')
def add_bill_extra(request, placement):
	if request.method == 'POST':
		placement = Placement.objects.get(pk=placement)
		admin = Administrator.objects.get(pk=request.session['admin'])
		price = request.POST.get('price', 0)
		quantity = request.POST.get('quantity', 1)
		name = request.POST.get('name', 'Extra')

		if placement.branch.pk != admin.branch.pk:
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant ', 405))

		if placement.waiter != None:
			if placement.waiter.pk != admin.pk != None and admin.admin_type == '4':
				return HttpJsonResponse(ResponseObject('error', 'Data Not For This Admin ', 405))

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
					currency=admin.restaurant.config.currency
				)
			new_bill.save()

			placement.bill = Bill.objects.get(pk=new_bill.pk)
			placement.save()

		placement = Placement.objects.get(pk=placement.pk)

		if placement.bill.is_paid:
			return HttpJsonResponse(ResponseObject('error', 'Bill Has Been Paid !!!', 405))

		bill_extra = BillExtra(
				bill=Bill.objects.get(pk=placement.bill.pk),
				price=price,
				quantity=quantity,
				name=name
			)
		bill_extra.save()
		return HttpJsonResponse(ResponseObject('success', 'Bill Extra Saved !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_admin_login
@is_admin_enabled
def delete_bill_extra(request, extra):
	admin = Administrator.objects.get(pk=request.session['admin'])
	extra = BillExtra.objects.get(pk=extra)

	placement = Placement.objects.get(pk=extra.bill.placement_id)

	if admin.restaurant.pk != placement.restaurant.pk or admin.branch.pk != placement.branch.pk:
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403))

	if placement.is_done:
		return HttpJsonResponse(ResponseObject('error', 'Placement Is Done !!!', 403))

	extra.delete()
	return HttpJsonResponse(ResponseObject('success', 'Extra Bill Deleted Successfully !!!', 200))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_done_placement')
def done_placement(request, token):
	placement = Placement.objects.filter(token=token).first()
	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != placement.restaurant.pk or admin.branch.pk != placement.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_placements')))

	if placement.bill != None:
		if placement.bill.is_paid == False or placement.bill.is_complete == False:
			messages.error(request, 'Bill Yet To Be Paid !!!')
			return HttpJsonResponse(ResponseObject('error', 'Bill Yet To Be Paid !!!', 403, 
				reverse('ting_wb_adm_placements')))

	placement.is_done = True
	placement.save()
	notify_user_placement_done.now(placement.pk)
	messages.success(request, 'Placement Ended Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Placement Ended Successfully !!!', 200, 
				reverse('ting_wb_adm_placements')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_done_placement')
def mark_bill_paid(request, placement):
	placement = Placement.objects.get(pk=placement)
	admin = Administrator.objects.get(pk=request.session['admin'])

	if admin.restaurant.pk != placement.restaurant.pk or admin.branch.pk != placement.branch.pk:
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403))

	if placement.bill != None:
		
		bill = Bill.objects.get(pk=placement.bill.pk)
		bill.is_complete = True
		bill.is_paid = True
		bill.paid_by = placement.user.pk
		bill.save()

		notify_user_bill_payed.now(placement.pk)
		return HttpJsonResponse(ResponseObject('success', 'Bill Marked As Paid !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bill Not Found !!!', 403))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_assign_table')
def assign_waiter_placement(request, token, waiter):
	placement = Placement.objects.filter(token=token).first()
	admin = Administrator.objects.get(pk=request.session['admin'])
	waiter = Administrator.objects.get(pk=waiter)

	if admin.restaurant.pk != placement.restaurant.pk or admin.branch.pk != placement.branch.pk or waiter.branch.pk != admin.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_placements')))

	placement.waiter = Administrator.objects.get(pk=waiter.pk)
	placement.save()
	notify_user_placement_waiter_assigned.now(placement.pk)
	messages.success(request, 'Waiter Assigned Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Waiter Assigned Successfully !!!', 200, 
				reverse('ting_wb_adm_placements')))


@background(schedule=60)
def notify_user_placement_done(placement):
	placement = Placement.objects.get(pk=placement)
	user_message = {
		'status': 200,
		'type': 'response_resto_placement_done',
		'uuid': pnconfig.uuid,
		'sender': placement.branch.socket_data,
		'receiver': placement.user.socket_data,
		'message': None,
		'args': None,
		'data': None
	}

	pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)

	try:
		pusher_client.trigger(placement.user.channel, placement.user.channel, {
			'title': 'Placement Terminated', 
			'body': 'Your placement of %s at %s, %s has been terminated' % (placement.created_at.strftime('%a %d %b, %Y'), placement.restaurant.name, placement.branch.name),
			'text': 'Your placement of %s at %s, %s has been terminated' % (placement.created_at.strftime('%a %d %b, %Y'), placement.restaurant.name, placement.branch.name),
			'navigate': 'placement_done',
			'data': None
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[placement.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Placement Terminated', 
							'body': 'Your placement of %s at %s, %s has been terminated' % (placement.created_at.strftime('%a %d %b, %Y'), placement.restaurant.name, placement.branch.name),
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Placement Terminated', 
						'body': 'Your placement of %s at %s, %s has been terminated' % (placement.created_at.strftime('%a %d %b, %Y'), placement.restaurant.name, placement.branch.name),
					},
					'data': {
						'navigate': 'placement_done',
						'data': None
					}
				}
			}
		)
	except Exception as e:
		pass


@background(schedule=60)
def notify_user_placement_waiter_assigned(placement):
	placement = Placement.objects.get(pk=placement)
	waiter_message = {
		'status': 200,
		'type': 'response_w_resto_table',
		'uuid': pnconfig.uuid,
		'sender': placement.branch.socket_data,
		'receiver': placement.waiter.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'user': placement.user.socket_data, 'table': placement.table.number }
	}

	pubnub.publish().channel(placement.waiter.channel).message(waiter_message).pn_async(ting_publish_callback)

	user_message = {
		'status': 200,
		'type': 'response_resto_table_waiter',
		'uuid': pnconfig.uuid,
		'sender': placement.branch.socket_data,
		'receiver': placement.user.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'waiter': placement.waiter.socket_data }
	}

	pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)

	send_pusher_notification(
		'New Table For You', 
		'You have been assigned to the client on table %s' % placement.table.number,
		placement.user.image.url, '', 'placement', placement.token, placement.waiter.channel)
	
	try:
		pusher_client.trigger(placement.user.channel, placement.user.channel, {
			'title': 'Your Waiter', 
			'body': 'You will be served today by %s' % placement.waiter.name,
			'image': utils.HOST_END_POINT + placement.waiter.image.url,
			'navigate': 'current_restaurant',
			'data': placement.token
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[placement.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Your Waiter', 
							'body': 'You will be served today by %s' % placement.waiter.name,
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Your Waiter', 
						'body': 'You will be served today by %s' % placement.waiter.name,
					},
					'data': {
						'navigate': 'current_restaurant',
						'data': placement.token
					}
				}
			}
		)
	except Exception as e:
		pass


@background(schedule=60)
def notify_user_bill_payed(placement):
	placement = Placement.objects.get(pk=placement)

	user_message = {
		'status': 200,
		'type': 'response_resto_bill_paid',
		'uuid': pnconfig.uuid,
		'sender': placement.branch.socket_data,
		'receiver': placement.user.socket_data,
		'message': None,
		'args': None,
		'data': {'token': placement.token, 'waiter': placement.waiter.socket_data }
	}

	pubnub.publish().channel(placement.user.channel).message(user_message).pn_async(ting_publish_callback)
	
	try:
		pusher_client.trigger(placement.user.channel, placement.user.channel, {
			'title': 'Bill Paid', 
			'body': 'Your bill No %s at %s, %s has been terminated and marked as paid.' % (placement.bill.number, placement.restaurant.name, placement.branch.name),
			'image': utils.HOST_END_POINT + placement.restaurant.logo.url,
			'navigate': 'current_restaurant',
			'data': placement.token
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[placement.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Bill Paid', 
							'body': 'Your bill No %s at %s, %s has been marked as paid.' % (placement.bill.number, placement.restaurant.name, placement.branch.name),
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Bill Paid', 
						'body': 'Your bill No %s at %s, %s has been marked as paid.' % (placement.bill.number, placement.restaurant.name, placement.branch.name),
					},
					'data': {
						'navigate': 'current_restaurant',
						'data': placement.token
					}
				}
			}
		)
	except Exception as e:
		pass


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_view_orders', 'can_receive_orders'])
def load_orders_dashboard(request):
	template = 'web/admin/ajax/load_orders_dashboard.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	orders = Order.objects.filter(menu__branch__pk=admin.branch.pk, menu__restaurant__pk=admin.restaurant.pk).filter(Q(is_delivered=False) & Q(is_declined=False)).order_by('updated_at')
	return render(request, template, {
			'orders': orders if admin.admin_type != '4' else list(filter(lambda od: od.bill.placement.waiter.pk == admin.pk, list(filter(lambda od: od.bill.placement.waiter != None, orders)))), 
			'admin': admin
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission=['can_view_orders', 'can_receive_orders'])
def load_user_placement_order(request, order):
	template = 'web/admin/ajax/load_user_placement_order.html'
	admin =  Administrator.objects.get(pk=request.session['admin'])
	order = Order.objects.get(pk=order)

	if order.menu.branch.pk != admin.branch.pk:
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant ', 405))

	return render(request, template, {'admin': admin, 'order': order})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_accept_orders')
def accept_user_order(request, order):
	admin = Administrator.objects.get(pk=request.session['admin'])
	order = Order.objects.get(pk=order)

	placement = Placement.objects.get(pk=order.bill.placement_id)

	if admin.restaurant.pk != order.menu.restaurant.pk or admin.branch.pk != order.menu.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
				reverse('ting_wb_adm_dashboard')))

	order.is_delivered = True
	order.save()

	notify_waiter_order_updated.now(placement.pk)
	notify_user_order_accepted.now(placement.pk, order.pk)
	messages.success(request, 'Order Accepted Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Order Accepted Successfully !!!', 200, 
				reverse('ting_wb_adm_dashboard')))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_accept_orders')
def decline_user_order(request, order):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		order = Order.objects.get(pk=order)
		reasons = request.POST.get('reasons')

		placement = Placement.objects.get(pk=order.bill.placement_id)

		if admin.restaurant.pk != order.menu.restaurant.pk or admin.branch.pk != order.menu.branch.pk:
			messages.error(request, 'Data Not For This Restaurant !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant !!!', 403, 
					reverse('ting_wb_adm_dashboard')))

		order.is_declined = True
		order.reasons = reasons
		order.save()

		notify_waiter_order_updated.now(placement.pk)
		notify_user_order_declined.now(placement.pk, order.pk)
		messages.success(request, 'Order Declined Successfully !!!')
		return HttpJsonResponse(ResponseObject('success', 'Order Declined Successfully !!!', 200, 
					reverse('ting_wb_adm_dashboard')))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@background(schedule=60)
def notify_user_order_accepted(placement, order):
	placement = Placement.objects.get(pk=placement)
	order = Order.objects.get(pk=order)
	try:
		pusher_client.trigger(placement.user.channel, placement.user.channel, {
			'title': 'Order Accepted', 
			'body': 'Your %s order(s) of %s has been accepted' % (order.quantity, order.menu.name),
			'image': utils.HOST_END_POINT + order.menu.images[0].image.url,
			'navigate': 'current_restaurant',
			'data': placement.token
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[placement.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Order Accepted', 
							'body': 'Your %s order(s) of %s has been accepted' % (order.quantity, order.menu.name),
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Order Accepted', 
						'body': 'Your %s order(s) of %s has been accepted' % (order.quantity, order.menu.name),
					},
					'data': {
						'navigate': 'current_restaurant',
						'data': placement.token
					}
				}
			}
		)
	except Exception as e:
		pass


@background(schedule=60)
def notify_user_order_declined(placement, order):
	placement = Placement.objects.get(pk=placement)
	order = Order.objects.get(pk=order)
	try:
		pusher_client.trigger(placement.user.channel, placement.user.channel, {
			'title': 'Order Declined', 
			'body': 'Your %s order(s) of %s has been declined' % (order.quantity, order.menu.name),
			'image': utils.HOST_END_POINT + order.menu.images[0].image.url,
			'text': 'Reasons: %s' % order.reasons,
			'navigate': 'current_restaurant',
			'data': placement.token
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[placement.user.channel],
			publish_body={
				'apns': {
					'aps': {
						'alert': {
							'title': 'Order Declined', 
							'body': 'Your %s order(s) of %s has been declined' % (order.quantity, order.menu.name),
						}
					}
				},
				'fcm': {
					'notification': {
						'title': 'Order Declined', 
						'body': 'Your %s order(s) of %s has been declined' % (order.quantity, order.menu.name),
					},
					'data': {
						'navigate': 'current_restaurant',
						'data': placement.token
					}
				}
			}
		)
	except Exception as e:
		pass


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


@check_admin_login
@is_admin_enabled
def get_admin_messages_count(request):
	admin = Administrator.objects.get(pk=request.session['admin'])
	messages = PlacementMessage.objects.filter(placement__waiter__pk=admin.pk, is_read=False).count()
	return HttpResponse(messages)


@check_admin_login
@is_admin_enabled
def load_admin_messages(request):
	template = 'web/admin/ajax/load_admin_messages.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	messages = PlacementMessage.objects.filter(placement__waiter__pk=admin.pk, is_read=False).order_by('created_at')
	return render(request, template, {'messages': messages})


@check_admin_login
@is_admin_enabled
def delete_admin_message(request, message):
	admin = Administrator.objects.get(pk=request.session['admin'])
	message = PlacementMessage.objects.get(pk=message)

	if message.placement.branch.pk != admin.branch.pk:
		messages.error(request, 'Data Not For This Restaurant !!!')
		return HttpJsonResponse(ResponseObject('error', 'Data Not For This Restaurant ', 405, 
				reverse('ting_wb_adm_dashboard')))

	if message.placement.waiter != None:
		if message.placement.waiter.pk != admin.pk != None and admin.admin_type == '4':
			messages.error(request, 'Data Not For This Waiter !!!')
			return HttpJsonResponse(ResponseObject('error', 'Data Not For This Admin ', 405, 
					reverse('ting_wb_adm_dashboard')))

	message.delete()
	messages.success(request, 'Order Declined Successfully !!!')
	return HttpJsonResponse(ResponseObject('success', 'Message Deleted Successfully !!!', 200, 
				reverse('ting_wb_adm_dashboard')))


def send_pusher_notification(title, body, image, text, navigate, data, channel):
	try:
		pusher_client.trigger(channel, channel, {
			'title': title, 
			'body': body,
			'image': utils.HOST_END_POINT + image if image != None else "",
			'text': text,
			'navigate': navigate,
			'data': data
		})
	except Exception as e:
		pass
				
	try:
		beams_client.publish_to_interests(
			interests=[channel],
			publish_body={
				'apns': { 'aps': { 'alert': { 'title': title, 'body': body } } },
				'fcm': {
					'notification': { 'title': title, 'body': body },
					'data': { 'navigate': navigate, 'data': data }
				}
			}
		)
	except Exception as e:
		pass



# REPORT


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_reports')
def reports_incomes(request):
	template = 'web/admin/reports_incomes.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	return render(request, template,  {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str)
		})


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def load_bills_income_reports(request):
	template = 'web/admin/ajax/load_bills_income_reports.html'
	admin = Administrator.objects.get(pk=request.session['admin'])

	selected_year = request.GET.get('year') if request.method == 'GET' else request.POST.get('year')
	selected_month = request.GET.get('month') if request.method == 'GET' else request.POST.get('month')
	selected_day = request.GET.get('day') if request.method == 'GET' else request.POST.get('day')

	selected_values = [selected_year, selected_month, selected_day]

	if any((True for value in selected_values if value != None and value != '')) == False:
		today = datetime.now()
		selected_year = today.year
		selected_month = today.month
		selected_day = today.day

	date_values = [ long(selected_year), int(selected_month), int(selected_day) ]

	if any((True for value in date_values if value == 0)) == True:
		if int(selected_day) == 0 and int(selected_month) != 0:
			date_string = '%s, %s' % (utils.get_month_name(int(selected_month)), selected_year)
			name_string = '%s_%s' % (utils.get_month_name(selected_month).lower(), selected_year)
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__month=int(selected_month),
													created_at__year=int(selected_year),
													bill__isnull=False).order_by('created_at')
		else:
			date_string, name_string = selected_year, selected_year
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__year=int(selected_year),
													bill__isnull=False).order_by('created_at')
	else:
		date = datetime.strptime('-'.join(map(lambda x: str(x), date_values)), '%Y-%m-%d')
		date_string = date.strftime('%A %d %B, %Y')
		name_string = date.strftime('%Y_%m_%d')
		placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
												branch__pk=admin.branch.pk, 
												created_at__date=date,
												bill__isnull=False).order_by('created_at')

	amounts_sum = sum(list(map(lambda placement: placement.bill.amount, placements)))
	discounts_sum = sum(list(map(lambda placement: placement.bill.discount, placements)))
	extras_sum = sum(list(map(lambda placement: placement.bill.extras_total, placements)))
	tips_sum = sum(list(map(lambda placement: placement.bill.tips, placements)))
	totals_sum = sum(list(map(lambda placement: placement.bill.total, placements)))
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'days': utils.get_days(),
			'months': utils.get_months(),
			'years': utils.get_years(),
			'selected_day': int(selected_day),
			'selected_month': int(selected_month),
			'selected_year': long(selected_year),
			'date_string': date_string,
			'placements': placements,
			'amounts_sum': amounts_sum,
			'discounts_sum': discounts_sum,
			'extras_sum': extras_sum,
			'tips_sum': tips_sum,
			'totals_sum': totals_sum,
			'random_uuid': get_random_string(10),
			'filename_pdf': 'placement_bills_%s.pdf' % name_string,
			'today': datetime.now().strftime('%A %d %B, %Y')
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def export_bills_income_reports_excel(request):
	admin = Administrator.objects.get(pk=request.session['admin'])

	selected_year = request.GET.get('year') if request.method == 'GET' else request.POST.get('year')
	selected_month = request.GET.get('month') if request.method == 'GET' else request.POST.get('month')
	selected_day = request.GET.get('day') if request.method == 'GET' else request.POST.get('day')

	selected_values = [selected_year, selected_month, selected_day]

	if any((True for value in selected_values if value != None and value != '')) == False:
		today = datetime.now()
		selected_year = today.year
		selected_month = today.month
		selected_day = today.day

	date_values = [ long(selected_year), int(selected_month), int(selected_day) ]

	if any((True for value in date_values if value == 0)) == True:
		if int(selected_day) == 0 and int(selected_month) != 0:
			date_string = '%s_%s' % (utils.get_month_name(selected_month).lower(), selected_year)
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__month=int(selected_month),
													created_at__year=int(selected_year),
													bill__isnull=False).annotate(created_date=Cast('created_at', DateField())).order_by('created_at')
		else:
			date_string = '%s' % selected_year
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__year=int(selected_year),
													bill__isnull=False).annotate(created_date=Cast('created_at', DateField())).order_by('created_at')
	else:
		date = datetime.strptime('-'.join(map(lambda x: str(x), date_values)), '%Y-%m-%d')
		date_string = date.strftime('%Y_%m_%d')
		placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
												branch__pk=admin.branch.pk, 
												created_at__date=date,
												bill__isnull=False).annotate(created_date=Cast('created_at', DateField())).order_by('created_at')

	export = request.GET.get('export') if request.method == 'GET' else request.POST.get('export')
		
	if export == 'csv':
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="placement_bills_%s.csv"' % date_string

		writer = csv.writer(response)
		writer.writerow(['Date', 'User', 'Table', 'People', 'Bill', 'Amount', 'Discount', 'Extras', 'Tips', 'Total', 'Currency'])

		for placement in placements.values_list('created_date', 'user__name', 'table__number', 'people', 'bill__number', 'bill__amount', 'bill__discount', 'bill__extras_total', 'bill__tips', 'bill__total', 'bill__currency'):
			writer.writerow(placement)

	else:
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="placement_bills_%s.xls"' % date_string

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Placements')

		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		columns = ['Date', 'User', 'Table', 'People', 'Bill', 'Amount', 'Discount', 'Extras', 'Tips', 'Total', 'Currency',]

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		font_style = xlwt.XFStyle()

		for placement in placements.values_list('created_date', 'user__name', 'table__number', 'people', 'bill__number', 'bill__amount', 'bill__discount', 'bill__extras_total', 'bill__tips', 'bill__total', 'bill__currency'):
			row_num += 1
			for col_num in range(len(placement)):
				ws.write(row_num, col_num, str(placement[col_num]), font_style)

		wb.save(response)

	return response


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def export_bills_income_reports_pdf(request):
	template = 'web/admin/reports/report_bills_income.html'
	admin = Administrator.objects.get(pk=request.session['admin'])

	selected_year = request.GET.get('year') if request.method == 'GET' else request.POST.get('year')
	selected_month = request.GET.get('month') if request.method == 'GET' else request.POST.get('month')
	selected_day = request.GET.get('day') if request.method == 'GET' else request.POST.get('day')

	selected_values = [selected_year, selected_month, selected_day]

	if any((True for value in selected_values if value != None and value != '')) == False:
		today = datetime.now()
		selected_year = today.year
		selected_month = today.month
		selected_day = today.day

	date_values = [ long(selected_year), int(selected_month), int(selected_day) ]

	if any((True for value in date_values if value == 0)) == True:
		if int(selected_day) == 0 and int(selected_month) != 0:
			date_string = '%s, %s' % (utils.get_month_name(int(selected_month)), selected_year)
			name_string = '%s_%s' % (utils.get_month_name(selected_month).lower(), selected_year)
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__month=int(selected_month),
													created_at__year=int(selected_year),
													bill__isnull=False).order_by('created_at')
		else:
			date_string, name_string = selected_year, selected_year
			placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
													branch__pk=admin.branch.pk, 
													created_at__year=int(selected_year),
													bill__isnull=False).order_by('created_at')
	else:
		date = datetime.strptime('-'.join(map(lambda x: str(x), date_values)), '%Y-%m-%d')
		date_string = date.strftime('%A %d %B, %Y')
		name_string = date.strftime('%Y_%m_%d')
		placements = Placement.objects.filter(restaurant__pk=admin.restaurant.pk, 
												branch__pk=admin.branch.pk, 
												created_at__date=date,
												bill__isnull=False).order_by('created_at')

	amounts_sum = sum(list(map(lambda placement: placement.bill.amount, placements)))
	discounts_sum = sum(list(map(lambda placement: placement.bill.discount, placements)))
	extras_sum = sum(list(map(lambda placement: placement.bill.extras_total, placements)))
	tips_sum = sum(list(map(lambda placement: placement.bill.tips, placements)))
	totals_sum = sum(list(map(lambda placement: placement.bill.total, placements)))

	data = {
				'admin': admin,
				'restaurant': admin.restaurant,
				'selected_day': int(selected_day),
				'selected_month': int(selected_month),
				'selected_year': long(selected_year),
				'date_string': date_string,
				'placements': placements,
				'amounts_sum': amounts_sum,
				'discounts_sum': discounts_sum,
				'extras_sum': extras_sum,
				'tips_sum': tips_sum,
				'totals_sum': totals_sum
		}

	pdf = utils.render_to_pdf(template, data)

	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="placement_bills_%s.pdf"' % name_string
	return response


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def load_bills_income_stats(request):
	template = 'web/admin/ajax/load_bills_income_stats.html'
	admin = Administrator.objects.get(pk=request.session['admin'])

	periods = [
				{'value': 1, 'key': 'Past Days'},
				{'value': 2, 'key': 'Past Months'},
				{'value': 3, 'key': 'Past Years'}
			]

	incomes_data = []

	custom = request.GET.get('custom') if request.method == 'GET' else request.POST.get('custom')
	period_number = request.GET.get('period_number') if request.method == 'GET' else request.POST.get('period_number')
	period = request.GET.get('period') if request.method == 'GET' else request.POST.get('period')
	custom_start_date = request.GET.get('custom_start_date') if request.method == 'GET' else request.POST.get('custom_start_date')
	custom_end_date = request.GET.get('custom_end_date') if request.method == 'GET' else request.POST.get('custom_end_date')
	custom_period = request.GET.get('custom_period') if request.method == 'GET' else request.POST.get('custom_period')

	use_custom = True if custom == 'on' else False

	if use_custom == False:

		date_list = utils.get_dates_days(int(period_number))
		months_list = utils.get_dates_months(int(period_number))
		years_list = utils.get_dates_years(int(period_number))

		if int(period_number) <= 0:
			return HttpJsonResponse(ResponseObject('error', 'Period Number Cannot Be Less or Equal To 0 !!!', 406))

		if int(period) == 1:
			date_string = 'For The Past %s Days - ( from %s to %s )' % (period_number, date_list[::-1][0].strftime('%d %b, %Y'), date_list[::-1][len(date_list) - 1].strftime('%d %b, %Y'))
			name_string = 'from_%s_to_%s' % (date_list[::-1][0].strftime('%Y_%m_%d'), date_list[::-1][len(date_list) - 1].strftime('%Y_%m_%d'))
			for date in date_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))

		elif int(period) == 2:
			date_string = 'For The Past %s Months - ( from %s to %s )' % (period_number, 
								'%s %s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
								'%s %s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
												'%s_%s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			for date in months_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))
		
		elif int(period) == 3:
			date_string = 'For The Past %s Years - ( from %s to %s )' % (period_number, years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			name_string = 'from_%s_to_%s' % (years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			for date in years_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))
	else:
		try:
			start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
			end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')

			if start_date > end_date:
				return HttpJsonResponse(ResponseObject('error', 'Start Date Cant Be Greater Than End Date !!!', 406))

			if int(custom_period) == 1:
				range_dates = utils.get_dates_range(start_date, end_date)
				date_string = 'From %s To %s' % (range_dates[::-1][0].strftime('%d %b, %Y'), range_dates[::-1][len(range_dates) - 1].strftime('%d %b, %Y'))
				name_string = 'from_%s_to_%s' % (range_dates[::-1][0].strftime('%Y_%m_%d'), range_dates[::-1][len(range_dates) - 1].strftime('%Y_%m_%d'))
				for date in range_dates:
					bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period)))

			elif int(custom_period) == 2:
				range_months = utils.get_months_range(start_date, end_date)
				date_string = 'From %s To %s' % ('%s %s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s %s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s_%s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				for date in range_months:
					bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True)
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period)))

		except ValueError as e:
			return HttpJsonResponse(ResponseObject('error', 'Insert Valid Dates !!!', 406))

	amounts_sum = sum(list(map(lambda income: income['amount'], incomes_data)))
	discounts_sum = sum(list(map(lambda income: income['discount'], incomes_data)))
	extras_sum = sum(list(map(lambda income: income['extras'], incomes_data)))
	tips_sum = sum(list(map(lambda income: income['tips'], incomes_data)))
	totals_sum = sum(list(map(lambda income: income['total'], incomes_data)))

	series = ['Count', 'Amount', 'Discount', 'Extras', 'Tips', 'Total']

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'random_uuid': get_random_string(10),
			'today': datetime.now().strftime('%A %d %B, %Y'),
			'periods': periods,
			'use_custom': use_custom,
			'period_number': period_number,
			'selected_period': period,
			'custom_start_date': custom_start_date,
			'custom_end_date': custom_end_date,
			'selected_custom_period': custom_period,
			'incomes': incomes_data,
			'i__dt__charts': json.dumps(incomes_data[::-1], default=str),
			'i__dt__series': json.dumps(series, default=str),
			'amounts_sum': amounts_sum,
			'discounts_sum': discounts_sum,
			'extras_sum': extras_sum,
			'tips_sum': tips_sum,
			'totals_sum': totals_sum,
			'date_string': date_string.replace('-', ''),
			'date_string_array': date_string.split('-'),
			'filename_pdf_stats': 'incomes_report_%s_stats.pdf' % name_string,
			'filename_pdf_charts': 'incomes_report_%s_charts.pdf' % name_string
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def export_bills_income_stats_excel(request):
	admin = Administrator.objects.get(pk=request.session['admin'])

	incomes_data = []

	custom = request.GET.get('custom') if request.method == 'GET' else request.POST.get('custom')
	period_number = request.GET.get('period_number') if request.method == 'GET' else request.POST.get('period_number')
	period = request.GET.get('period') if request.method == 'GET' else request.POST.get('period')
	custom_start_date = request.GET.get('custom_start_date') if request.method == 'GET' else request.POST.get('custom_start_date')
	custom_end_date = request.GET.get('custom_end_date') if request.method == 'GET' else request.POST.get('custom_end_date')
	custom_period = request.GET.get('custom_period') if request.method == 'GET' else request.POST.get('custom_period')

	use_custom = True if custom == 'True' else False

	if use_custom == False:

		date_list = utils.get_dates_days(int(period_number))
		months_list = utils.get_dates_months(int(period_number))
		years_list = utils.get_dates_years(int(period_number))

		if int(period) == 1:
			date_string = 'from_%s_to_%s' % (date_list[::-1][0].strftime('%Y_%m_%d'), date_list[::-1][len(date_list) - 1].strftime('%Y_%m_%d'))
			for date in date_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period), False))

		elif int(period) == 2:
			date_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][1]), 
												'%s_%s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][1]))
			for date in months_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period), False))
		
		elif int(period) == 3:
			date_string = 'from_%s_to_%s' % (years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			for date in years_list:
				bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, is_paid=True)
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period), False))
	else:
		try:
			start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
			end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')

			if int(custom_period) == 1:
				range_dates = utils.get_dates_range(start_date, end_date)
				date_string = 'from_%s_to_%s' % (range_dates[::-1][0].strftime('%Y_%m_%d'), range_dates[::-1][len(range_dates) - 1].strftime('%Y_%m_%d'))
				for date in range_dates:
					bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, is_paid=True)
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period), False))

			elif int(custom_period) == 2:
				range_months = utils.get_months_range(start_date, end_date)
				date_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][1]), 
													'%s_%s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][1]))
				for date in range_months:
					bills_date = Bill.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], is_paid=True)
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period), False))

		except ValueError as e:
			pass

	export = request.GET.get('export') if request.method == 'GET' else request.POST.get('export')
	columns = ['Date', 'Count', 'Amount', 'Discount', 'Discount Number', 'Extras', 'Extras Number', 'Tips', 'Tips Number', 'Total', 'Currency']

	ordered_data = list(map(lambda data: [
						data['date'], data['count'], data['amount'], data['discount'],
						data['count_discount'], data['extras'], data['count_extras'], data['tips'],
						data['count_tips'], data['total'], admin.restaurant.config.currency], incomes_data))[::-1]

	if export == 'csv':
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="incomes_report_%s.csv"' % date_string.lower()

		writer = csv.writer(response)
		writer.writerow(columns)

		for data in ordered_data:
			writer.writerow(data)

	else:
		response = HttpResponse(content_type='application/ms-excel')
		response['Content-Disposition'] = 'attachment; filename="incomes_report_%s.xls"' % date_string.lower()

		wb = xlwt.Workbook(encoding='utf-8')
		ws = wb.add_sheet('Placements')

		row_num = 0

		font_style = xlwt.XFStyle()
		font_style.font.bold = True

		for col_num in range(len(columns)):
			ws.write(row_num, col_num, columns[col_num], font_style)

		font_style = xlwt.XFStyle()

		for data in ordered_data:
			row_num += 1
			for col_num in range(len(data)):
				ws.write(row_num, col_num, str(data[col_num]), font_style)

		wb.save(response)

	return response


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_reports')
def reports_waiters(request):
	template = 'web/admin/reports_waiters.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	waiters = Administrator.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, admin_type=4).order_by('name')
	return render(request, template,  {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str),
			'waiters': waiters
		})


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def load_waiter_reports(request, waiter):
	template = 'web/admin/ajax/load_waiter_reports.html'
	waiter = get_object_or_404(Administrator, pk=waiter)

	admin = Administrator.objects.get(pk=request.session['admin'])

	periods = [
				{'value': 1, 'key': 'Past Days'},
				{'value': 2, 'key': 'Past Months'},
				{'value': 3, 'key': 'Past Years'}
			]

	incomes_data = []

	custom = request.GET.get('custom') if request.method == 'GET' else request.POST.get('custom')
	period_number = request.GET.get('period_number') if request.method == 'GET' else request.POST.get('period_number')
	period = request.GET.get('period') if request.method == 'GET' else request.POST.get('period')
	custom_start_date = request.GET.get('custom_start_date') if request.method == 'GET' else request.POST.get('custom_start_date')
	custom_end_date = request.GET.get('custom_end_date') if request.method == 'GET' else request.POST.get('custom_end_date')
	custom_period = request.GET.get('custom_period') if request.method == 'GET' else request.POST.get('custom_period')

	use_custom = True if custom == 'on' else False

	if use_custom == False:

		date_list = utils.get_dates_days(int(period_number))
		months_list = utils.get_dates_months(int(period_number))
		years_list = utils.get_dates_years(int(period_number))

		if int(period_number) <= 0:
			return HttpJsonResponse(ResponseObject('error', 'Period Number Cannot Be Less or Equal To 0 !!!', 406))

		if int(period) == 1:
			date_string = 'For The Past %s Days - ( from %s to %s )' % (period_number, date_list[::-1][0].strftime('%d %b, %Y'), date_list[::-1][len(date_list) - 1].strftime('%d %b, %Y'))
			name_string = 'from_%s_to_%s' % (date_list[::-1][0].strftime('%Y_%m_%d'), date_list[::-1][len(date_list) - 1].strftime('%Y_%m_%d'))
			for date in date_list:
				bills_date = list(map(lambda placement: placement.bill, Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, bill__isnull=False, waiter__isnull=False, waiter__pk=waiter.pk)))
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))

		elif int(period) == 2:
			date_string = 'For The Past %s Months - ( from %s to %s )' % (period_number, 
								'%s %s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
								'%s %s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
												'%s_%s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			for date in months_list:
				bills_date = list(map(lambda placement: placement.bill, Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], bill__isnull=False, waiter__isnull=False, waiter__pk=waiter.pk)))
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))
		
		elif int(period) == 3:
			date_string = 'For The Past %s Years - ( from %s to %s )' % (period_number, years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			name_string = 'from_%s_to_%s' % (years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			for date in years_list:
				bills_date = list(map(lambda placement: placement.bill, Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date, bill__isnull=False, waiter__isnull=False, waiter__pk=waiter.pk)))
				incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(period)))
	else:
		try:
			start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
			end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')

			if start_date > end_date:
				return HttpJsonResponse(ResponseObject('error', 'Start Date Cant Be Greater Than End Date !!!', 406))

			if int(custom_period) == 1:
				range_dates = utils.get_dates_range(start_date, end_date)
				date_string = 'From %s To %s' % (range_dates[::-1][0].strftime('%d %b, %Y'), range_dates[::-1][len(range_dates) - 1].strftime('%d %b, %Y'))
				name_string = 'from_%s_to_%s' % (range_dates[::-1][0].strftime('%Y_%m_%d'), range_dates[::-1][len(range_dates) - 1].strftime('%Y_%m_%d'))
				for date in range_dates:
					bills_date = list(map(lambda placement: placement.bill, Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__date=date, bill__isnull=False, waiter__isnull=False, waiter__pk=waiter.pk)))
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period)))

			elif int(custom_period) == 2:
				range_months = utils.get_months_range(start_date, end_date)
				date_string = 'From %s To %s' % ('%s %s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s %s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s_%s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				for date in range_months:
					bills_date = lis(map(lambda placement: placement.bill, Placement.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk, created_at__year=date[0], created_at__month=date[1], bill__isnull=False, waiter__isnull=False, waiter__pk=waiter.pk)))
					incomes_data.append(utils.generate_incomes_dict(date, bills_date, int(custom_period)))

		except ValueError as e:
			return HttpJsonResponse(ResponseObject('error', 'Insert Valid Dates !!!', 406))

	amounts_sum = sum(list(map(lambda income: income['amount'], incomes_data)))
	discounts_sum = sum(list(map(lambda income: income['discount'], incomes_data)))
	extras_sum = sum(list(map(lambda income: income['extras'], incomes_data)))
	tips_sum = sum(list(map(lambda income: income['tips'], incomes_data)))
	totals_sum = sum(list(map(lambda income: income['total'], incomes_data)))

	series = ['Count', 'Amount', 'Tips', 'Total']

	return render(request, template, {
			'waiter': waiter,
			'admin': admin,
			'restaurant': admin.restaurant,
			'random_uuid': get_random_string(10),
			'today': datetime.now().strftime('%A %d %B, %Y'),
			'periods': periods,
			'use_custom': use_custom,
			'period_number': period_number,
			'selected_period': period,
			'custom_start_date': custom_start_date,
			'custom_end_date': custom_end_date,
			'selected_custom_period': custom_period,
			'incomes': incomes_data,
			'i__dt__charts': json.dumps(incomes_data[::-1], default=str),
			'i__dt__series': json.dumps(series, default=str),
			'amounts_sum': amounts_sum,
			'discounts_sum': discounts_sum,
			'extras_sum': extras_sum,
			'tips_sum': tips_sum,
			'totals_sum': totals_sum,
			'date_string': date_string.replace('-', ''),
			'date_string_array': date_string.split('-'),
			'filename_pdf_stats': '%s_incomes_report_%s_stats.pdf' % (waiter.username, name_string),
			'filename_pdf_charts': '%s_incomes_report_%s_charts.pdf' % (waiter.username, name_string)
		})


@check_admin_login
@is_admin_enabled
@subscribe_ting_socket
@has_admin_permissions(permission='can_view_reports')
def reports_menus(request):
	template = 'web/admin/reports_menus.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	menus = Menu.objects.filter(branch__pk=admin.branch.pk, restaurant__pk=admin.restaurant.pk)
	return render(request, template,  {
			'admin': admin,
			'restaurant': admin.restaurant,
			'admin_json': json.dumps(admin.to_json, default=str),
			'menus': menus
		})


@csrf_exempt
@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_reports')
def load_menu_reports(request, menu):
	template = 'web/admin/ajax/load_menu_reports.html'
	menu = get_object_or_404(Menu, pk=menu)

	admin = Administrator.objects.get(pk=request.session['admin'])

	periods = [
				{'value': 1, 'key': 'Past Days'},
				{'value': 2, 'key': 'Past Months'},
				{'value': 3, 'key': 'Past Years'}
			]

	incomes_data = []

	custom = request.GET.get('custom') if request.method == 'GET' else request.POST.get('custom')
	period_number = request.GET.get('period_number') if request.method == 'GET' else request.POST.get('period_number')
	period = request.GET.get('period') if request.method == 'GET' else request.POST.get('period')
	custom_start_date = request.GET.get('custom_start_date') if request.method == 'GET' else request.POST.get('custom_start_date')
	custom_end_date = request.GET.get('custom_end_date') if request.method == 'GET' else request.POST.get('custom_end_date')
	custom_period = request.GET.get('custom_period') if request.method == 'GET' else request.POST.get('custom_period')

	use_custom = True if custom == 'on' else False

	if use_custom == False:

		date_list = utils.get_dates_days(int(period_number))
		months_list = utils.get_dates_months(int(period_number))
		years_list = utils.get_dates_years(int(period_number))

		if int(period_number) <= 0:
			return HttpJsonResponse(ResponseObject('error', 'Period Number Cannot Be Less or Equal To 0 !!!', 406))

		if int(period) == 1:
			date_string = 'For The Past %s Days - ( from %s to %s )' % (period_number, date_list[::-1][0].strftime('%d %b, %Y'), date_list[::-1][len(date_list) - 1].strftime('%d %b, %Y'))
			name_string = 'from_%s_to_%s' % (date_list[::-1][0].strftime('%Y_%m_%d'), date_list[::-1][len(date_list) - 1].strftime('%Y_%m_%d'))
			for date in date_list:
				orders_date = Order.objects.filter(bill__branch__pk=admin.branch.pk, bill__restaurant__pk=admin.restaurant.pk, menu__pk=menu.pk, created_at__date=date, is_delivered=True)
				incomes_data.append(utils.generate_orders_dict(date, orders_date, int(period)))

		elif int(period) == 2:
			date_string = 'For The Past %s Months - ( from %s to %s )' % (period_number, 
								'%s %s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
								'%s %s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(months_list[::-1][0][1]), months_list[::-1][0][0]), 
												'%s_%s' % (utils.get_month_name(months_list[::-1][len(months_list) - 1][1]), months_list[::-1][len(months_list) - 1][0]))
			for date in months_list:
				orders_date = Order.objects.filter(bill__branch__pk=admin.branch.pk, bill__restaurant__pk=admin.restaurant.pk, menu__pk=menu.pk, created_at__year=date[0], created_at__month=date[1], is_delivered=True)
				incomes_data.append(utils.generate_orders_dict(date, orders_date, int(period)))
		
		elif int(period) == 3:
			date_string = 'For The Past %s Years - ( from %s to %s )' % (period_number, years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			name_string = 'from_%s_to_%s' % (years_list[::-1][0], years_list[::-1][len(years_list) - 1])
			for date in years_list:
				orders_date = Order.objects.filter(bill__branch__pk=admin.branch.pk, bill__restaurant__pk=admin.restaurant.pk, menu__pk=menu.pk, created_at__year=date, is_delivered=True)
				incomes_data.append(utils.generate_orders_dict(date, orders_date, int(period)))
	else:
		try:
			start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
			end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')

			if start_date > end_date:
				return HttpJsonResponse(ResponseObject('error', 'Start Date Cant Be Greater Than End Date !!!', 406))

			if int(custom_period) == 1:
				range_dates = utils.get_dates_range(start_date, end_date)
				date_string = 'From %s To %s' % (range_dates[::-1][0].strftime('%d %b, %Y'), range_dates[::-1][len(range_dates) - 1].strftime('%d %b, %Y'))
				name_string = 'from_%s_to_%s' % (range_dates[::-1][0].strftime('%Y_%m_%d'), range_dates[::-1][len(range_dates) - 1].strftime('%Y_%m_%d'))
				for date in range_dates:
					orders_date = Order.objects.filter(bill__branch__pk=admin.branch.pk, bill__restaurant__pk=admin.restaurant.pk, menu__pk=menu.pk, created_at__date=date, is_delivered=True)
					incomes_data.append(utils.generate_orders_dict(date, orders_date, int(custom_period)))

			elif int(custom_period) == 2:
				range_months = utils.get_months_range(start_date, end_date)
				date_string = 'From %s To %s' % ('%s %s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s %s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				name_string = 'from_%s_to_%s' % ('%s_%s' % (utils.get_month_name(range_months[::-1][0][1]), range_months[::-1][0][0]), 
													'%s_%s' % (utils.get_month_name(range_months[::-1][len(range_months) - 1][1]), range_months[::-1][len(range_months) - 1][0]))
				for date in range_months:
					orders_date = Order.objects.filter(bill__branch__pk=admin.branch.pk, bill__restaurant__pk=admin.restaurant.pk, menu__pk=menu.pk, created_at__year=date[0], created_at__month=date[1], is_delivered=True)
					incomes_data.append(utils.generate_orders_dict(date, orders_date, int(custom_period)))

		except ValueError as e:
			return HttpJsonResponse(ResponseObject('error', 'Insert Valid Dates !!!', 406))

	totals_sum = sum(list(map(lambda income: income['total'], incomes_data)))
	quantity_sum = sum(list(map(lambda income: income['quantity'], incomes_data)))
	counts_sum = sum(list(map(lambda income: income['count'], incomes_data)))
	price_average = sum(list(map(lambda income: income['price'] if income['price'] > 0 else menu.price, incomes_data))) / len(incomes_data)

	series = ['Count', 'Quantity', 'Total']

	return render(request, template, {
			'menu': menu,
			'admin': admin,
			'restaurant': admin.restaurant,
			'random_uuid': get_random_string(10),
			'today': datetime.now().strftime('%A %d %B, %Y'),
			'periods': periods,
			'use_custom': use_custom,
			'period_number': period_number,
			'selected_period': period,
			'custom_start_date': custom_start_date,
			'custom_end_date': custom_end_date,
			'selected_custom_period': custom_period,
			'incomes': incomes_data,
			'i__dt__charts': json.dumps(incomes_data[::-1], default=str),
			'i__dt__series': json.dumps(series, default=str),
			'totals_sum': totals_sum,
			'quantity_sum': quantity_sum,
			'counts_sum': counts_sum,
			'price_average': price_average,
			'date_string': date_string.replace('-', ''),
			'date_string_array': date_string.split('-'),
			'filename_pdf_stats': '%s_incomes_report_%s_stats.pdf' % (menu.name.replace(' ', '_').lower(), name_string),
			'filename_pdf_charts': '%s_incomes_report_%s_charts.pdf' % (menu.name.replace(' ', '_').lower(), name_string)
		})