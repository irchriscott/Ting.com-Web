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
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.models import (
							Restaurant, Administrator, AdminPermission, RestaurantLicenceKey, RestaurantConfig,
							Menu, Food, Drink, Dish, FoodCategory, FoodImage, AdministratorResetPassword
						)
from tingweb.backend import AdminAuthentication
from tingweb.mailer import (SendAdminRegistrationMail, SendAdminResetPasswordMail)
from tingweb.forms import (
							RestaurantUpdateLogo, RestaurantUpdateProfile, RestaurantUpdateConfig, 
							AdministratorUpdateImage, AdministratorUpdateProfile, AdministratorUpdateUsername, 
							AdministratorUpdateEmail, AddAdministrator, FoodCategoryForm, EditFoodCategoryForm,
							AddMenuFood, FoodImageForm, EditMenuFood
						) 
import ting.utils as utils
from datetime import datetime, timedelta
import tingadmin.permissions as permissions


# Create your views here.


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
				messages.error(request, 'Sorry, Your Account Has Been Disabled !!! !!!')
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


class AdminLogin(TemplateView):

	template = 'web/admin/login.html'

	def get(self, request, *args, **kwargs):
		if 'admin' in request.session.keys():
			return HttpResponseRedirect(reverse('ting_wb_adm_dashboard'))
		return render(request, self.template, {})

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
				return HttpJsonResponse(ResponseObject('error', 'Invalid Email or Password !!!', 400))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


def logout(request):
	try:
		del request.session['admin']
		messages.success(request, 'Admin Logged Out Successfully !!!')
		return HttpResponseRedirect(reverse('ting_wb_adm_login'))
	except KeyError:
		messages.error(request, 'No Admin Session Found !!!')
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
			return HttpJsonResponse(ResponseObject('error', 'Unknown Administrator Email', 400))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


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

					messages.success(request, 'Password Updated Successfully !!!')
					return HttpResponseRedirect(reverse('ting_wb_adm_login'))
				else:
					messages.error(request, 'Passwords Didnt Match !!!')
					return HttpResponseRedirect(link)
			else:
				messages.error(request, 'Bad Request !!!')
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
			'restaurant': admin.restaurant
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
						return HttpJsonResponse(ResponseObject('error', 'This Licence Key Has Expired !!!', 400))
				else:
					return HttpJsonResponse(ResponseObject('info', 'You Have Already Activated This Key !!!', 400, 
							reverse('ting_wb_adm_dashboard')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Licence Key Not Found !!!', 400))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Key !!!', 400))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
def dashboard(request):
	template = 'web/admin/dashboard.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	key = RestaurantLicenceKey.objects.filter(restaurant=admin.restaurant.pk).last()

	if admin.restaurant.is_authenticated is False:
		return HttpResponseRedirect(reverse('ting_wb_adm_welcome'))
	if key.is_active == False:
		return HttpResponseRedirect(reverse('ting_wb_adm_welcome'))

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant
		})


# Restaurant And Configurations


@check_admin_login
@is_admin_enabled
def restaurant(request):
	template = 'web/admin/restaurant.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	currencies = utils.CURRENCIES
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'currencies': currencies
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
			
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Logo Updated Successfully !!!', 200))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Image !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


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
				
				restaurant = Restaurant.objects.get(pk=admin.restaurant.pk)
				restaurant.name = form.cleaned_data['name']
				restaurant.branch = form.cleaned_data['branch']
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
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


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
				config.updated_at = timezone.now()
				config.save()

				messages.success(request, 'Restaurant Config Updated Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Restaurant Config Updated Successfully !!!', 200, 
							reverse('ting_wb_adm_restaurant')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
@is_admin_enabled
def administrators(request):
	template = 'web/admin/administrators.html'	
	admin = Administrator.objects.get(pk=request.session['admin'])
	administrators = admin.restaurant.administrators
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'administrators': administrators,
			'types': utils.ADMIN_TYPE	
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
			'types': types
		})


# Administrators


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

		form = AddAdministrator(request.POST, instance=Administrator(
				restaurant=Restaurant.objects.get(pk=session.restaurant.pk),
				token=admin_token,
				image=utils.DEFAULT_ADMIN_IMAGE,
				password=make_password(password)
			))

		if form.is_valid() and password != '':
			if check_password(request.POST.get('password'), session.password) == True:

				admin = form.save()

				_permissions = []

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
						'password': password
					})
				mail.send()

				messages.success(request, 'Administrator Created Successfully !!!')
				return HttpJsonResponse(ResponseObject('success', 'Administrator Created Successfully', 200, 
						reverse('ting_wb_adm_administrators')))
			else:
				return HttpJsonResponse(ResponseObject('error', 'Incorrect Password !!!', 401))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


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
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


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

				if admin.username != request.POST.get('username'):
					if username.is_valid():
						admin.username = username.cleaned_data['username']
					else:
						return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=username.errors.items()))

				if admin.email != request.POST.get('email'):
					if email.is_valid():
						admin.email = email.cleaned_data['email']
					else:
						return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=email.errors.items()))
				
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
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_disable_admin', xhr='ajax')
def disable_admin_account_toggle(request, token):
	admin = Administrator.objects.get(token=token)
	session = Administrator.objects.get(pk=request.session['admin'])
	if admin.pk != session.pk:
		if admin.is_disabled == False:
			admin.is_disabled = True
			admin.updated_at = timezone.now()
			admin.save()
		
			messages.success(request, 'Administrator Account Disabled !!!')
			return HttpJsonResponse(ResponseObject('success', 'Administrator Account Disabled !!!', 200, 
					reverse('ting_wb_adm_administrators')))
		elif admin.is_valid == True:
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
def admin_security(request):
	template = 'web/admin/security.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant
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
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


# Permissions


@check_admin_login
@is_admin_enabled
def admin_permissions(request):
	template = 'web/admin/permissions.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	return render(request, template, {
			'admin': admin,
			'restaurants': permissions.restaurant,
			'tables': permissions.tables,
			'administrators': permissions.administrators,
			'category': permissions.category,
			'menus': permissions.menus,
			'orders': permissions.orders,
			'bills': permissions.bills,
			'booking': permissions.booking,
			'management': permissions.management,
			'restaurant': admin.restaurant
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_admin')
def edit_admin_permissions(request, token):
	template = 'web/admin/ajax/load_permissions_admin.html'
	admin = Administrator.objects.get(token=token)
	return render(request, template, {
			'admin': admin,
			'restaurant': permissions.restaurant,
			'tables': permissions.tables,
			'administrators': permissions.administrators,
			'category': permissions.category,
			'menus': permissions.menus,
			'orders': permissions.orders,
			'bills': permissions.bills,
			'booking': permissions.booking,
			'management': permissions.management
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
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


# Categories


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_category')
def categories(request):
	template = 'web/admin/categories.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	categories = FoodCategory.objects.all()
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'categories': categories
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
				slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-'), get_random_string(16)).lower()
			))

		if form.is_valid():

			form.save()

			messages.success(request, 'Category Created Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Category Created Successfully !!!', 200, 
					reverse('ting_wb_adm_categories')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_delete_category', xhr='ajax')
def delete_category(request, slug):
	admin = Administrator.objects.get(pk=request.session['admin'])
	category = FoodCategory.objects.get(slug=slug)
	
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

		if form.is_valid():

			category = FoodCategory.objects.get(slug=slug)
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
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


# Menus Food


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def menu_food(request):
	template = 'web/admin/menu_food.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	foods = Food.objects.all().order_by('-created_at')
	categories = FoodCategory.objects.all()
	types = utils.FOOD_TYPE
	currencies = utils.CURRENCIES

	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'foods': foods,
			'categories': categories,
			'types': types,
			'currencies': currencies
		})


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_add_menu', xhr='ajax')
def add_new_menu_food(request):
	if request.method == 'POST':
		admin = Administrator.objects.get(pk=request.session['admin'])
		is_countable = True if request.POST.get('is_countable') is 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') is 'on' else False

		form = AddMenuFood(request.POST, instance=Food(
				restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
				admin=Administrator.objects.get(pk=admin.pk),
				slug='{0}-{1}'.format(request.POST.get('name').replace(' ', '-'), get_random_string(16)).lower(),
				category=FoodCategory.objects.get(pk=request.POST.get('category')),
				is_countable=is_countable,
				show_ingredients=show_ingredients,
				quantity=int(request.POST.get('quantity')) if is_countable is True else 1
			))

		images_form = FoodImageForm(request.POST, request.FILES)

		if form.is_valid() and images_form.is_valid():

			food = form.save()
			images = request.FILES.getlist('image')

			for image in images:
				img = FoodImage(
						food=Food.objects.get(pk=food.pk),
						image=image
					)
				img.save()

			menu = Menu(
					restaurant=Restaurant.objects.get(pk=admin.restaurant.pk),
					admin=Administrator.objects.get(pk=admin.pk),
					menu_type=utils.MENU_TYPE[0][0],
					menu_id=food.pk
				)
			menu.save()

			messages.success(request, 'Menu Food Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Food Added Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_avail_menu', xhr='ajax')
def avail_menu_food_toggle(request, pk):
	food = get_object_or_404(Food, pk=pk)
	food.admin = Administrator.objects.get(pk=request.session['admin'])
	food.updated_at = timezone.now()

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
		is_countable = True if request.POST.get('is_countable') is 'on' else False
		show_ingredients = True if request.POST.get('show_ingredients') is 'on' else False

		food = get_object_or_404(Food, pk=food)
		form = EditMenuFood(request.POST)

		if form.is_valid():

			food.name = form.cleaned_data['name']
			food.description = form.cleaned_data['description']
			food.last_price = form.cleaned_data['last_price']
			food.price = form.cleaned_data['price']
			food.currency = form.cleaned_data['currency']
			food.ingredients = form.cleaned_data['ingredients']
			food.is_countable = is_countable
			food.show_ingredients = show_ingredients
			food.quantity = int(request.POST.get('quantity')) if is_countable == True else 1
			food.admin = Administrator.objects.get(pk=admin.pk)
			food.updated_at = timezone.now()

			food.save()

			images = request.FILES.getlist('image')

			if len(images) > 0:
				for image in images:
					img = FoodImage(
							food=Food.objects.get(pk=food.pk),
							image=image
						)
					img.save()

			menu = Menu.objects.filter(menu_type=1, menu_id=food.pk).first()
			menu.admin = Administrator.objects.get(pk=admin.pk)
			menu.updated_at = timezone.now()
			menu.save()

			messages.success(request, 'Menu Food Updated Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Menu Food Updated Successfully !!!', 200, 
					reverse('ting_wb_adm_menu_food')))
		else:
			return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 400, msgs=form.errors.items() + images_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def delete_menu_food_image(request, food, image):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)
	image = get_object_or_404(FoodImage, pk=image)

	if food.images.count() > 2:
		image.delete()
		return HttpJsonResponse(ResponseObject('success', 'Menu Food Image Deleted Successfully !!!', 200))
	else:
		return HttpJsonResponse(ResponseObject('error', 'The Menu Food Must Have More Than 2 Images To Perform This Action !!!', 400))



@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_update_menu', xhr='ajax')
def delete_menu_food(request, food):
	admin = Administrator.objects.get(pk=request.session['admin'])
	food = get_object_or_404(Food, pk=food)

	return HttpJsonResponse(ResponseObject('info', 'Action To Be Implemented Later !!!', 500))



# Menu Drinks


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def menu_drinks(request):
	template = 'web/admin/menu_drinks.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	menus = []
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'menus': menus
		})


# Menus Dishes


@check_admin_login
@is_admin_enabled
@has_admin_permissions(permission='can_view_menu')
def menu_dishes(request):
	template = 'web/admin/menu_dishes.html'
	admin = Administrator.objects.get(pk=request.session['admin'])
	menus = []
	return render(request, template, {
			'admin': admin,
			'restaurant': admin.restaurant,
			'menus': menus
		})
