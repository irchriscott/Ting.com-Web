# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, request
from django.urls import reverse
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from tingadmin.backend import UserAuthentication
from tingadmin.models import RestaurantCategory, TingPackage, TingLicenceKey
from ting.responses import ResponseObject, HttpJsonResponse
from tingadmin.forms import RestaurantCategoryForm, RestaurantFormAdmin, TingPackageForm, BranchForm
from tingweb.models import Restaurant, RestaurantConfig, Administrator, AdminPermission, RestaurantLicenceKey, Branch
from tingadmin.mailer import SendRestaurantRegistrationMail
import ting.utils as utils
import datetime
import tingadmin.permissions as permissions

# Create your views here.

def check_admin_login(func):
    def wrapper(request, *args, **kwargs):
        if 'ting' not in request.session.keys():
            messages.error(request, 'Login Required, Please !!!')
            return HttpResponseRedirect(reverse('ting_admin_login'))
        return func(request, *args, **kwargs)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

class AdminLogin(TemplateView):

    template = 'admin/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template, {})

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            auth = UserAuthentication(email=email, password=password)

            if auth.authenticate != None:
                request.session['ting'] = auth.authenticate.pk
                messages.success(request, 'Admin Logged In Successfully !!!')
                return HttpResponseRedirect(reverse('ting_admin_dashboard'))
            else:
                messages.error(request, 'Invalid Email or Password !!!')
                return HttpResponseRedirect(reverse('ting_admin_login'))
            pass
        else:
            messages.error(request, 'Bad Request')
            return HttpResponseRedirect(reverse('ting_admin_login'))


def logout(request):
	try:
		del request.session['ting']
		messages.success(request, 'Admin Logged Out Successfully !!!')
		return HttpResponseRedirect(reverse('ting_admin_login'))
	except KeyError:
		messages.error(request, 'No Admin Session Found !!!')
		return HttpResponseRedirect(reverse('ting_admin_login'))



@check_admin_login
def dashboard(request):
	template = 'admin/dashboard.html'
	restaurants = Restaurant.objects.all().order_by('-created_at')
	return render(request, template, {'restaurants': restaurants})


@check_admin_login
def restaurants(request):
	template = 'admin/dashboard.html'
	restaurants = Restaurant.objects.all().order_by('-created_at')
	return render(request, template, {'restaurants': restaurants})


@check_admin_login
def add_restaurant(request):
	if request.method == 'POST':
		
		token = get_random_string(128)
		slug = '%s-%s'.lower() % (request.POST.get('name').replace(' ', '-'), get_random_string(16))
		email = request.POST.get('email')
		phone = request.POST.get('phone')

		# Create Restaurant
		
		restaurant_form = RestaurantFormAdmin(request.POST, instance=Restaurant(
				token=token,
				slug=slug,
				logo=utils.DEFAULT_RESTAURANT_IMAGE
			))

		branch_form = BranchForm(request.POST, instance=Branch(
				name=request.POST.get('branch')
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
					image=utils.DEFAULT_ADMIN_IMAGE,
					phone=phone
				)

			admin.save()

			# Administrator Permissions

			_permissions = AdminPermission(
					admin=Administrator.objects.get(pk=admin.pk),
					permissions=','.join(permissions.admin_permissions)
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

			messages.success(request, 'Restaurant Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Restaurant Added Successfully !!!', 200, 
                reverse('ting_admin_dashboard')))
		else:
			return HttpJsonResponse(
                ResponseObject('error', 'Fill All Fields With Rignt Data, Please !!!', 400, msgs=restaurant_form.errors.items() + branch_form.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
def categories(request):
	template = 'admin/categories.html'
	categories = RestaurantCategory.objects.all().order_by('created_at')
	return render(request, template, {'categories': categories})


@check_admin_login
def add_category(request):
	if request.method == 'POST':
		category = RestaurantCategoryForm(request.POST)
		if category.is_valid():
			category.save()
			messages.success(request, 'Category Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Category Added Successfully !!!', 200, 
                reverse('ting_admin_categories')))
		else:
			return HttpJsonResponse(
                ResponseObject('error', 'Fill All Fields With Rignt Data, Please !!!', 400, msgs=category.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))



@check_admin_login
def delete_category(request, id):
	if request.method == 'POST':
		category = RestaurantCategory.objects.get(pk=id)
		if category:
			category.delete()
			messages.success(request, 'Category Deleted Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Category Deleted Successfully !!!', 200, 
                reverse('ting_admin_categories')))
		else:
			return HttpJsonResponse(
                ResponseObject('error', 'Unknown Category', 400))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))


@check_admin_login
def packages(request):
	template = 'admin/packages.html'
	packages = TingPackage.objects.all()
	currencies = utils.CURRENCIES
	return render(request, template, {'packages': packages, 'currencies': currencies})


@check_admin_login
def add_package(request):
	if request.method == 'POST':
		admin = User.objects.get(pk=request.session['ting'])
		package = TingPackageForm(request.POST, request.FILES, instance=TingPackage())

		if package.is_valid():
			package.save()
			messages.success(request, 'Package Added Successfully !!!')
			return HttpJsonResponse(ResponseObject('success', 'Package Added Successfully !!!', 200, 
                reverse('ting_admin_packages')))
		else:
			return HttpJsonResponse(
                ResponseObject('error', 'Fill All Fields With Rignt Data, Please !!!', 400, msgs=package.errors.items()))
	else:
		return HttpJsonResponse(ResponseObject('error', 'Bad Request', 400))

