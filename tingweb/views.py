# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, get_object_or_404
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
                                Food, Dish, Drink, FoodCategory
                            )
from tingweb.forms import (
                                GoogleSignUpForm, UserLocationForm, EmailSignUpForm, UserImageForm, MenuReviewForm,
                                RestaurantReviewForm, ReservationForm
                            )
from tingadmin.models import RestaurantCategory
import ting.utils as utils
from datetime import datetime, timedelta
from functools import reduce
import operator
import json
import imgkit
import os
import re
import random


# Create your views here.


def check_user_login(xhr=None):
    def decorator_wrapper(func):
        def wrapper(request, *args, **kwargs):
            if 'user' not in request.session.keys():
                if request.method == 'POST' or request.is_ajax() or xhr == 'ajax':
                    return HttpJsonResponse(ResponseObject('error', 'Login Required !!!', 401))
                else:
                    messages.error(request, 'Login Required !!!')
                    return HttpResponseRedirect(reverse('ting_index'))
            
            return func(request, *args, **kwargs)
        
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    
    return decorator_wrapper


# USER LOGIN, SIGNUP & PROFILE


@csrf_exempt
def sign_up_with_google(request):
    if request.method == 'POST':
        user_form = GoogleSignUpForm(request.POST, instance=User(
                image=utils.DEFAULT_USER_IMAGE,
                username='%s_%s' % (request.POST.get('name').replace(' ', '_').lower(), str(random.randint(1, 101))),
                phone='',
                channel=get_random_string(64)
            ))
        token = request.POST.get('token')
        email = request.POST.get('email')

        token_id = token.split('-')[0]
        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_index')

        try:
            check_user = User.objects.get(email=email)
            if 'user' in request.session:
                if request.session['user'] == check_user.pk:
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link, user=check_user.to_json))
            else:
                if check_user.token.split('-')[0] == token_id:
                    try:
                        if len(check_user.token.split('-')[1]) < 128:
                            check_user.token = '%s-%s' %(check_user.token.split('-')[0], get_random_string(512))
                            check_user.updated_at = timezone.now()
                            check_user.save()
                    except KeyError as e:
                        pass
                    
                    request.session['user'] = check_user.pk
                    messages.success(request, 'User Logged In Successfully !!!')
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link, user=check_user.to_json))
                else:
                    check_user.token = token
                    check_user.updated_at = timezone.now()
                    check_user.save()
                    request.session['user'] = check_user.pk
                    
                    messages.success(request, 'User Logged In Successfully !!!')
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link, user=check_user.to_json, msgs=[]))

        except User.DoesNotExist:
            address_form = UserLocationForm(request.POST)

            if address_form.is_valid() and user_form.is_valid():
                user = user_form.save()
                address = address_form.save(commit=False)
                address.user = User.objects.get(pk=user.pk)
                address.save()
                request.session['user'] = user.pk
                get_user_map_pin_svg(request, user.pk, False)
                messages.success(request, 'User Signed In Successfully !!!')
                return HttpJsonResponse(ResponseObject('success', 'User Signed In Successfully !!!', 200, link, user=user.to_json, msgs=[]))
            else:
                return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                        msgs=user_form.errors.items() + address_form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def sign_up_with_email(request):
    if request.method == 'POST':
        user_form = EmailSignUpForm(request.POST, instance=User(
                token=get_random_string(512),
                image=utils.DEFAULT_USER_IMAGE,
                phone='',
                channel=get_random_string(64)
            ))

        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_index')
        address_form = UserLocationForm(request.POST)

        if request.POST.get('type').lower() == 'other' and (request.POST.get('other_address_type') == None or request.POST.get() == ''):
            return HttpJsonResponse(ResponseObject('error', 'You Selected Address As Other. Please, Enter The Other Type Of Address !!!', 406))

        try:
            bd = datetime.strptime(request.POST.get('date_of_birth'), '%Y-%m-%d')
            if bd > datetime.now():
                HttpJsonResponse(ResponseObject('error', 'Insert Valid Birth Date !!!', 406))
        except ValueError as e:
            return HttpJsonResponse(ResponseObject('error', 'Insert Valid Birth Date !!!', 406))

        if address_form.is_valid() and user_form.is_valid():
            user = user_form.save(commit=False)
            user.password = make_password(request.POST.get('password'))
            user.save()
            address = address_form.save(commit=False)
            address.user = User.objects.get(pk=user.pk)
            address.type = request.POST.get('other_address_type') if request.POST.get('type').lower() == 'other' else request.POST.get('type')
            address.save()
            request.session['user'] = user.pk
            get_user_map_pin_svg(request, user.pk, False)
            messages.success(request, 'User Registered Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'User Registered Successfully !!!', 200, link, user=user.to_json, msgs=[]))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=user_form.errors.items() + address_form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        auth = UserAuthentication(email=email, password=password)
        link = request.POST.get('link') if request.POST.get('link') != None else reverse('ting_index')

        if auth.authenticate != None:
            request.session['user'] = auth.authenticate.pk
            messages.success(request, 'User Logged In Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link, user=auth.authenticate.to_json, msgs=[]))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Invalid Email or Password !!!', 404))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def submit_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            reset = UserResetPassword(
                    user=User.objects.get(pk=user.pk),
                    email=email,
                    token=get_random_string(32),
                    expired_at=datetime.now() + timedelta(hours=24)
                )
            reset.save()

            mail = SendUserResetPasswordMail(email=email, context={
                    'name': user.name,
                    'link': reverse('ting_usr_reset_pwd_link', kwargs={'token':reset.token})
                })
            mail.send()

            return HttpJsonResponse(ResponseObject('success', 'Reset Password Link Mail Sent Successfully !!!', 200))

        except User.DoesNotExist as e:
            return HttpJsonResponse(ResponseObject('error', 'Unknown User Email', 404))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def reset_password_link(request, token):
    try:
        reset = UserResetPassword.objects.get(token=token)
        if reset.is_active == True:
            template = 'web/user/reset_password.html'
            return render(request, template, {'token': token})
        else:
            messages.error(request, 'Link Has Expired !!!')
            return HttpResponseRedirect(reverse('ting_index'))
    except UserResetPassword.DoesNotExist as e:
        messages.error(request, 'Invalid Token !!!!')
        return HttpResponseRedirect(reverse('ting_index'))


def reset_password(request, token):
    try:
        reset = UserResetPassword.objects.get(token=token)
        link = reverse('ting_usr_reset_pwd_link', kwargs={'token':token})
        if reset.is_active == True:
            if request.method == 'POST':
                password = request.POST.get('password')
                conf_password = request.POST.get('confirm_password')

                if password == conf_password:
                    user = User.objects.get(pk=reset.user.pk)
                    user.password = make_password(password)
                    user.updated_at = timezone.now()
                    user.save()

                    reset.is_active = False
                    reset.save()

                    mail = SendUserSuccessResetPasswordMail(email=user.email, context={
                            'name': user.name,
                            'link': reverse('ting_wb_adm_login'),
                            'ip': request.POST.get('ip'),
                            'location': request.POST.get('addr'),
                            'time': timezone.now(),
                            'tz': request.POST.get('tz'),
                            'os': request.POST.get('os')
                        })
                    mail.send()

                    messages.success(request, 'Password Updated Successfully !!!')
                    return HttpResponseRedirect(reverse('ting_index'))
                else:
                    messages.error(request, 'Passwords Didnt Match !!!')
                    return HttpResponseRedirect(link)
            else:
                messages.error(request, 'Method Not Allowed !!!')
                return HttpResponseRedirect(link)
        else:
            messages.error(request, 'Link Has Expired !!!')
            return HttpResponseRedirect(reverse('ting_index'))
    except UserResetPassword.DoesNotExist as e:
        messages.error(request, 'Invalid Token !!!!')
        return HttpResponseRedirect(reverse('ting_index'))


def logout(request):
    link = request.GET.get('href') if request.GET.get('href') != None else reverse('ting_index')
    try:
        del request.session['user']
        messages.success(request, 'User Logged Out Successfully !!!')
        return HttpResponseRedirect(link)
    except KeyError:
        messages.error(request, 'No User Session Found !!!')
        return HttpResponseRedirect(reverse(link))


# User Profile

@check_user_login(xhr='GET')
def user_profile(request, user, username):
    template = 'web/user/user/user_profile.html'
    user = get_object_or_404(User, pk=user)
    
    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))
    
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'user_json': json.dumps(user.to_json, default=str),
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


@check_user_login(xhr='ajax')
def update_user_profile_image(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        form = UserImageForm(request.POST, request.FILES)

        if form.is_valid():
            user.image = form.cleaned_data['image']
            user.updated_at = timezone.now()
            user.save()
            get_user_map_pin_svg(request, user.pk, False)
            return HttpJsonResponse(ResponseObject('success', 'User Image Updated Successfully !!!', 200, user=user.to_json))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Image !!!', 400, msgs=form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def get_user_map_pin_svg(request, user, create=True):
    template = 'web/user/user/map_pin_svg.html'
    user = User.objects.get(pk=user)
    
    logo = user.image.url
    data = logo.split('/')
    last = data[len(data) - 1]
    filename = '%s.svg' % last.split('.')[0]
    
    f = open(os.path.join(settings.MEDIA_ROOT, 'users', 'pins', filename), 'w+')
    f.write(
            """<?xml version="1.0" encoding="utf-8"?>
                <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <path stroke-width="2" stroke-miterlimit="10" stroke="#b56fe8" fill="#b56fe8" d="M55.9 28.3c.1-.8.1-1.5.1-2.3a24 24 0 0 0-48 0c0 .8 0 1.6.1 2.3v.3C10.1 47.6 32 61 32 61s21.9-13.6 23.8-32.3z" data-name="layer2" stroke-linejoin="round" stroke-linecap="round"></path>
                    <defs>
                        <pattern id="image" x="0" y="0" patternUnits="userSpaceOnUse" height="64" width="64">
                            <image height="40" width="40" x="12" y="6" xlink:href="%s"></image>
                        </pattern>
                    </defs>
                    <circle stroke-width="2" stroke-miterlimit="10" stroke="#b56fe8" fill="url(#image)" r="17" cy="26" cx="32" data-name="layer1" stroke-linejoin="round" stroke-linecap="round"></circle>
                </svg>
            """ % user.get_cover_base64()
        )
    f.close()
    if create == True:
        return render(request, template, {'user':user})


@check_user_login(xhr='ajax')
def update_user_password(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        conf_password = request.POST.get('confirm_password')

        if check_password(old_password, user.password) == True or old_password == None:
            if conf_password == new_password:
                user.password = make_password(conf_password)
                user.updated_at = timezone.now()
                user.save()

                return HttpJsonResponse(ResponseObject('success', 'User Password Updated Successfully !!!', 200, user=user.to_json))
            else:
                return HttpJsonResponse(ResponseObject('error', 'Passwords Didnt Match !!!', 400))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Wrong Old Password !!!', 400))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def update_user_email(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        
        password = request.POST.get('password')
        old_email = request.POST.get('old_email')
        new_email = request.POST.get('new_email')

        check_emails = User.objects.filter(email=new_email).count()

        if check_emails == 0:
            if check_password(user.password, password) == True:
                if old_email == user.email:
                    user.email = new_email
                    user.updated_at = timezone.new()
                    user.save()

                    mail = SendUserUpdateEmailMail(email=user.email, context={
                            'name': user.name,
                            'link': reverse('ting_wb_adm_login'),
                            'ip': request.POST.get('ip'),
                            'location': request.POST.get('addr'),
                            'time': timezone.now(),
                            'tz': request.POST.get('tz'),
                            'os': request.POST.get('os'),
                            'old_email': old_email
                        })
                    mail.send()

                    return HttpJsonResponse(ResponseObject('success', 'User Email Updated Successfully !!!', 200, user=user.to_json))
                else:
                    return HttpJsonResponse(ResponseObject('error', 'Passwords Didnt Match !!!', 400))
            else:
                return HttpJsonResponse(ResponseObject('error', 'Wrong Password !!!', 400))
        else:
            return HttpJsonResponse(ResponseObject('error', 'This Email Is Taken !!!', 400))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def update_user_private(request):
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

        user.date_of_birth = dob if dob != None or dob != '' else ''
        user.updated_at = timezone.now()
        user.save()

        return HttpJsonResponse(ResponseObject('success', 'User Private Info Updated Successfully !!!', 200))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def update_user_public(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        
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
        user.updated_at = timezone.now()
        user.save()

        return HttpJsonResponse(ResponseObject('success', 'User Private Info Updated Successfully !!!', 200))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def add_user_address(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        
        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_index')
        address_form = UserLocationForm(request.POST)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = User.objects.get(pk=user.pk)
            address.type = request.POST.get('other_address_type') if request.POST.get('type').lower() == 'other' else request.POST.get('type')
            address.save()
            
            messages.success(request, 'Address Added Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'Address Added Successfully !!!', 200, link, user=user.to_json))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=address_form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def load_user_edit_address(request, address):
    template = 'web/user/user/load_user_edit_address.html'
    user = User.objects.get(pk=request.session['user'])
    address = get_object_or_404(UserAddress, pk=address)
    
    if user.pk != address.user.pk:
        return HttpJsonResponse(ResponseObject('error', 'Address Does Not Belong To You !!!', 403))

    return render(request, template, {
            'user': user,
            'address': address,
            'address_types': utils.USER_ADDRESS_TYPE,
            'address_types_else': utils.USER_ADDRESS_TYPE_LIST
        })


@check_user_login(xhr='ajax')
def update_user_address(request, address):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        address = get_object_or_404(UserAddress, pk=address)

        if user.pk != address.user.pk:
            return HttpJsonResponse(ResponseObject('error', 'Address Does Not Belong To You !!!', 403))
        
        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_usr_profile', kwargs={'user':user.pk,'username':user.username})
        address_form = UserLocationForm(request.POST)

        if address_form.is_valid():
            address.address = address_form.cleaned_data['address']
            address.longitude = address_form.cleaned_data['longitude']
            address.latitude = address_form.cleaned_data['latitude']
            address.type = request.POST.get('other_address_type') if request.POST.get('type').lower() == 'other' else request.POST.get('type')
            address.updated_at = timezone.now()
            address.save()

            messages.success(request, 'Address Updated Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'Address Updated Successfully !!!', 200, link, user=user.to_json))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=address_form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def delete_user_address(request, address):
    user = User.objects.get(pk=request.session['user'])
    address = get_object_or_404(UserAddress, pk=address)
    
    if user.pk != address.user.pk:
        return HttpJsonResponse(ResponseObject('error', 'Address Does Not Belong To You !!!', 403))

    addresses = UserAddress.objects.filter(user__pk=user.id).count()

    if addresses > 1:
        address.delete()
        messages.success(request, 'Address Deleted Successfully !!!')
        return HttpJsonResponse(ResponseObject('success', 'Address Deleted Successfully !!!', 200, 
                reverse('ting_usr_profile', kwargs={'user':user.pk, 'username':user.username}), user=user.to_json))
    else:
        messages.error(request, 'You Need At Least 1 Address !!!')
        return HttpJsonResponse(ResponseObject('error', 'You Need At Least 1 Address !!!', 403, 
                reverse('ting_usr_profile', kwargs={'user':user.pk, 'username':user.username})))


def user_moments(request, user, username):
    template = 'web/user/user/user_moments.html'
    user = get_object_or_404(User, pk=user)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'user_json': json.dumps(user.to_json, default=str),
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


def user_restaurants(request, user, username):
    template = 'web/user/user/user_restaurants.html'
    user = get_object_or_404(User, pk=user)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'user_json': json.dumps(user.to_json, default=str),
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


@check_user_login(xhr='GET')
def user_orders(request, user, username):
    template = 'web/user/user/user_orders.html'
    user = get_object_or_404(User, pk=user)

    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'user_json': json.dumps(user.to_json, default=str),
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


@check_user_login(xhr='GET')
def user_bookings(request, user, username):
    template = 'web/user/user/user_bookings.html'
    user = get_object_or_404(User, pk=user)

    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'user_json': json.dumps(user.to_json, default=str),
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


def load_user_restaurants(request, user):
    template = 'web/user/user/load_user_restaurants.html'
    restaurants = UserRestaurant.objects.filter(user__pk=user)
    return render(request, template, {'restaurants': restaurants})


@check_user_login(xhr='ajax')
def make_reservation(request, restaurant, branch):
    if request.method == 'POST':
        restaurant = Restaurant.objects.get(pk=restaurant)
        branch = Branch.objects.get(pk=branch)
        booking = ReservationForm(request.POST, instance=Booking(
                user=User.objects.get(pk=request.session['user']),
                restaurant=Restaurant.objects.get(pk=restaurant.pk),
                branch=Branch.objects.get(pk=branch.pk),
                token=get_random_string(100)
            ))

        if restaurant.purpose != 2 or branch.is_available == False:
            return HttpJsonResponse(ResponseObject('error', 'Restaurant Doesnt Support This Feature !!!', 406))

        bk_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
        date = datetime.now() + timedelta(days=restaurant.config.days_before_reservation)

        if bk_date < date:
            return HttpJsonResponse(ResponseObject('error', 'Booking date should be %s days from now !!!' % str(restaurant.config.days_before_reservation), 406))

        if 'M' in request.POST.get('time'):
            times = re.findall(r'\d{1,2}(:\d{1,2})?(AM|PM)?', request.POST.get('time'))
            time = datetime.strptime(request.POST.get('time'), '%I:%M %p').time()
        else:
            time = datetime.strptime(request.POST.get('time'), '%H:%M').time()

        if time <= restaurant.opening or time >= restaurant.closing:
            return HttpJsonResponse(ResponseObject('error', 'Booking time should be between %s and %s !!!' % (restaurant.opening, restaurant.closing), 406))

        if booking.is_valid():
            reservation = booking.save(commit=False)
            reservation.time = time
            reservation.save()
            return HttpJsonResponse(ResponseObject('success', 'Reservation Booked Successfully !!!', 200))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=booking.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def load_user_reservations(request, user):
    template = 'web/user/user/load_user_reservations.html'
    reservations =  Booking.objects.filter(user__pk=request.session['user']).order_by('-updated_at')
    return render(request, template, {'reservations': reservations})


@check_user_login(xhr='ajax')
def load_edit_reservation(request, reservation):
    book = Booking.objects.get(pk=reservation)
    
    if book.user.pk != request.session['user']:
        return HttpJsonResponse(ResponseObject('error', 'Unauthorized !!!', 401))
    
    if book.status == 2 or book.status == 1:
        template = 'web/user/user/load_edit_reservation.html'
        return render(request, template, {'reservation': book, 'restaurant': book.branch, 'table_locations': utils.TABLE_LOCATION})
    else: 
        return HttpJsonResponse(ResponseObject('error', 'Cannot Update This Reservation For It Is %s !!!' % book.status_str, 401))


@check_user_login(xhr='ajax')
def update_reservation(request, reservation):
    if request.method == 'POST':
        booking = Booking.objects.get(pk=reservation)
        restaurant = booking.restaurant
        form = ReservationForm(request.POST)
        link = request.POST.get('link')

        if booking.user.pk != request.session['user']:
            return HttpJsonResponse(ResponseObject('error', 'Unauthorized !!!', 401))

        if booking.status != 2 and booking.status != 1:
            return HttpJsonResponse(ResponseObject('error', 'Cannot Update This Reservation For It Is %s !!!' % booking.status_str, 401))
        
        bk_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
        date = datetime.now() + timedelta(days=restaurant.config.days_before_reservation)

        if bk_date < date:
            return HttpJsonResponse(ResponseObject('error', 'Booking date should be %s from now !!!' % str(restaurant.config.days_before_reservation), 406))

        time = datetime.strptime(request.POST.get('time'), '%I:%M %p').time()

        if time <= restaurant.opening or time >= restaurant.closing:
            return HttpJsonResponse(ResponseObject('error', 'Booking time should be between %s and %s !!!' % (restaurant.opening, restaurant.closing), 406))

        if form.is_valid():
            booking.status = 1
            booking.people = form.cleaned_data['people']
            booking.date = form.cleaned_data['date']
            booking.time = time
            booking.location = form.cleaned_data['location']
            booking.updated_at = timezone.now()
            booking.save()

            messages.success(request, 'Reservation Updated Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'Reservation Updated Successfully !!!', 200, link))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=booking.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def cancel_reservation(request, reservation):
    booking = Booking.objects.get(pk=reservation)

    if booking.user.pk != request.session['user']:
        return HttpJsonResponse(ResponseObject('error', 'Unauthorized !!!', 401))

    if booking.status != 5 and booking.status != 6:
        return HttpJsonResponse(ResponseObject('error', 'This Reservation Is Completed !!!', 401))
        
    booking.status = 7 if booking.restaurant.config.booking_cancelation_refund == True else 6
    booking.updated_at = timezone.now()
    booking.save()

    url = reverse('ting_usr_bookings', kwargs={'user': booking.user.pk, 'username': booking.user.username})
    return HttpJsonResponse(ResponseObject('success', 'Reservation Canceled Successfully !!!', 200, url))
        
        
# GLOBAL LINKS


def index(request):
    template = 'web/index.html'
    cuisines = RestaurantCategory.objects.all()
    is_logged_in = True if 'user' in request.session else False

    if is_logged_in == True:
        user = User.objects.get(pk=request.session['user'])
        branches = Branch.objects.filter(country=user.country, town=user.town).order_by('-created_at')[:20]
        rand_branches = branches.random(5)

        promotions = Promotion.objects.filter(branch__country=user.country, branch__town=user.town, is_on=True)[:20]
        try:
            today_promos = random.sample(list(filter(lambda promo: promo.is_on_today == True, promotions))[:10], k=4)
        except Exception:
            today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))[:10]
    else:
        branches = Branch.objects.all().order_by('-created_at')[:20]
        rand_branches = branches.random(5)

        promotions = Promotion.objects.filter(is_on=True)[:5]
        try:
            today_promos = random.sample(list(filter(lambda promo: promo.is_on_today == True, promotions))[:10], k=4)
        except Exception:
            today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))[:10]

    menus_all = Menu.objects.all()
    menus = sorted(sorted(list(filter(lambda menu: menu.review_average >= 4, menus_all)), key=lambda menu: menu.reviews_count, reverse=True), key=lambda menu: menu.review_average, reverse=True)[:6]
    reviews = RestaurantReview.objects.filter(review__gte=4).random(10)

    return render(request, template, {
            'address_types': utils.USER_ADDRESS_TYPE,
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'cuisines': cuisines,
            'recommanded_branches': rand_branches,
            'recommanded_promotions': today_promos,
            'menus': menus,
            'reviews': sorted(reviews, key=lambda review: review.review, reverse=True)
        })


def discovery(request):
    template = 'web/user/global_discovery.html'
    cuisines = RestaurantCategory.objects.all()
    is_logged_in = True if 'user' in request.session else False

    if is_logged_in == True:
        user = User.objects.get(pk=request.session['user'])
        branches = Branch.objects.filter(country=user.country, town=user.town).order_by('-created_at')[:20]
        rand_branches = branches.random(5)

        promotions = Promotion.objects.filter(branch__country=user.country, branch__town=user.town, is_on=True)[:20]
        try:
            today_promos = random.sample(list(filter(lambda promo: promo.is_on_today == True, promotions))[:10], k=4)
        except Exception:
            today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))[:10]

        menus_all = Menu.objects.filter(branch__country=user.country, branch__town=user.town)
    else:
        branches = Branch.objects.all().order_by('-created_at')[:20]
        rand_branches = branches.random(5)

        promotions = Promotion.objects.filter(is_on=True)[:5]
        try:
            today_promos = random.sample(list(filter(lambda promo: promo.is_on_today == True, promotions))[:10], k=4)
        except Exception:
            today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))[:10]

        menus_all = Menu.objects.all()

    menus = sorted(sorted(list(filter(lambda menu: menu.review_average >= 4, menus_all)), key=lambda menu: menu.reviews_count, reverse=True), key=lambda menu: menu.review_average, reverse=True)[:10]
    reviews = RestaurantReview.objects.filter(review__gte=4).random(10)

    return render(request, template, {
            'is_logged_in': is_logged_in,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'cuisines': cuisines,
            'recommanded_branches': rand_branches,
            'recommanded_promotions': today_promos,
            'menus': menus,
            'reviews': sorted(reviews, key=lambda review: review.review, reverse=True)
        })


def discover_cuisine_restaurants(request, cuisine, slug):
    template = 'web/user/discovery/cuisine_restaurants.html'
    cuisine = RestaurantCategory.objects.get(pk=cuisine)
    branches = list(sorted(set(cuisine.restaurants), key=lambda branch: branch.review_average, reverse=True))

    page = request.GET.get('page', 1)
    paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)

    try:
        branches_all = paginator.page(page)
    except PageNotAnInteger:
        branches_all = paginator.page(1)
    except EmptyPage:
        branches_all = paginator.page(paginator.num_pages)

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'cuisine': cuisine,
            'branches': branches_all,
            'cuisines': RestaurantCategory.objects.exclude(pk=cuisine.pk).random(4)
        })


def discover_cuisine_menus(request, cuisine, slug):
    template = 'web/user/discovery/cuisine_menus.html'
    cuisine = RestaurantCategory.objects.get(pk=cuisine)
    foods = [food.menu for food in Food.objects.filter(cuisine__pk=cuisine.pk)]
    dishes = [dish.menu for dish in Dish.objects.filter(cuisine__pk=cuisine.pk)]
    _menus = foods + dishes

    menus = list(sorted(set(_menus), key=lambda menu: menu.to_json['menu']['reviews']['average'], reverse=True))

    page = request.GET.get('page', 1)
    paginator = Paginator(menus, settings.PAGINATOR_ITEM_COUNT)

    try:
        menus_all = paginator.page(page)
    except PageNotAnInteger:
        menus_all = paginator.page(1)
    except EmptyPage:
        menus_all = paginator.page(paginator.num_pages)

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'cuisine': cuisine,
            'menus': menus_all,
            'cuisines': RestaurantCategory.objects.exclude(pk=cuisine.pk).random(4)
        })


def discover_today_promotions(request):
    template = 'web/user/discovery/today_promotions.html'
    is_logged_in = True if 'user' in request.session else False

    if is_logged_in == True:
        user = User.objects.get(pk=request.session['user'])
        promotions = Promotion.objects.filter(branch__country=user.country, branch__town=user.town, is_on=True)
        today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))
    else:
        promotions = Promotion.objects.filter(is_on=True)
        today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))

    page = request.GET.get('page', 1)
    paginator = Paginator(today_promos, settings.PAGINATOR_ITEM_COUNT)

    try:
        promos = paginator.page(page)
    except PageNotAnInteger:
        promos = paginator.page(1)
    except EmptyPage:
        promos = paginator.page(paginator.num_pages)

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'promotions_json': json.dumps([promo.to_json for promo in promos], default=str),
            'promotions': promos,
            'menus': Menu.objects.random(len(promos) + 2)
        })


def restaurants(request):
    template = 'web/user/global_restaurants.html'
    branches = Branch.objects.all()
    paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'branches': json.dumps([branch.to_json_s for branch in branches], default=str),
            'countries': json.dumps(list(Branch.objects.values('country').annotate(branches=Count('country'))), default=str),
            'towns': json.dumps(list(Branch.objects.values('town', 'country').annotate(branches=Count('town'))), default=str),
            'cuisines': json.dumps([category.to_json for category in RestaurantCategory.objects.all()], default=str),
            'specials': json.dumps(utils.RESTAURANT_SPECIALS, default=str),
            'services': json.dumps(utils.RESTAURANT_SERVICES, default=str),
            'types': json.dumps(utils.RESTAURANT_TYPES, default=str),
            'filters': json.dumps(utils.generate_filter_data(), default=str),
            'num_pages': paginator.num_pages
        })


def filter_restaurants(request):
    
    country = request.POST.get('country', 'all') if request.method == 'POST' else 'all'
    query = request.POST.get('query', '') if request.method == 'POST' else ''
    
    restaurants = Branch.objects.filter(country=country).filter(Q(restaurant__name__icontains=query) | Q(name__icontains=query)) \
                    if country != 'all' else \
                        Branch.objects.filter(Q(restaurant__name__icontains=query) | Q(name__icontains=query))

    if request.POST.get('filters') != None:
        
        filters = json.loads(request.POST.get('filters'))

        brs__avail = list(map(lambda b: int(b.pk), list(filter(lambda b: b.availability in filters['availability'], restaurants))))
        brs__cuisines = list(map(lambda b: int(b.pk), list(filter(lambda b: any((True for c in filters['cuisines'] if c in map(lambda v: int(v), b.restaurant.categories_ids))), restaurants))))
        brs__services = list(map(lambda b: int(b.pk), list(filter(lambda b: any((True for s in filters['services'] if s in map(lambda v: int(v), b.services_ids))), restaurants))))
        brs__specials = list(map(lambda b: int(b.pk), list(filter(lambda b: any((True for s in filters['specials'] if s in map(lambda v: int(v), b.specials_ids))), restaurants))))
        brs__types = list(map(lambda b: int(b.pk), list(filter(lambda b: b.restaurant_type in filters['types'], restaurants))))
        brs__ratings = list(map(lambda b: int(b.pk), list(filter(lambda b: b.review_average in filters['ratings'], restaurants))))

        brs__f__all = [brs__avail, brs__cuisines, brs__services, brs__specials, brs__types, brs__ratings]
        brs__k__all = [filters['availability'], filters['cuisines'], filters['services'], filters['specials'], filters['types'], filters['ratings']]
        
        brs__ids__pts = [brs[0] for brs in zip(*[bs for i, bs in enumerate(brs__f__all) if len(brs__k__all[i]) != 0]) if len(set(brs)) == 1]
        brs__ids__all = brs__ids__pts if len(list(filter(lambda b: len(list(b)) != 0, brs__f__all))) != len(list(brs__f__all)) else list(reduce(lambda x, y: x & y, (set(brs) for i, brs in enumerate(brs__f__all) if len(list(brs__k__all[i])) != 0)))

        branches = restaurants.filter(pk__in=brs__ids__all) if len(list(filter(lambda f: len(f) != 0, brs__k__all))) != 0 else restaurants
    else:
        branches = restaurants
    
    page = request.POST.get('page', 1)
    paginator = Paginator(branches, settings.PAGINATOR_ITEM_COUNT)
    
    if paginator.num_pages >= int(page):
        try:
            _branches = json.dumps([paginator.num_pages, page, [branch.to_json_s for branch in paginator.page(page)]], default=str)
        except PageNotAnInteger:
            _branches = json.dumps([paginator.num_pages, page, [branch.to_json_s for branch in paginator.page(1)]], default=str)
        except EmptyPage:
            _branches = json.dumps([paginator.num_pages, page, [branch.to_json_s for branch in paginator.page(paginator.num_pages)]], default=str)
    else:
        _branches = json.dumps([paginator.num_pages, page, []], default=str)

    return HttpResponse(_branches, content_type='application/json')


def filter_restaurants_search(request):
    resto = request.POST.get('resto') if request.POST.get('resto') != None else ''
    branch = request.POST.get('branch') if request.POST.get('branch') != None else ''
    country = request.POST.get('country')

    branches = Branch.objects.filter(country=country).filter(
                Q(restaurant__name__icontains=resto) | 
                Q(name__icontains=branch) | 
                Q(tags__icontains=branch)) if country != 'all' else Branch.objects.filter(
                    Q(restaurant__name__icontains=resto) | 
                    Q(name__icontains=branch) | 
                    Q(tags__icontains=branch))

    return HttpJsonResponse([branch.to_json_r for branch in branches])


def get_filter_data(request):
    data = utils.generate_filter_data(request.GET.get('country'), None, request.GET.get('query'))
    return HttpResponse(json.dumps(data, default=str), content_type='application/json')


def moments(request):
    template = 'web/user/global_moments.html'
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


def blogs(request):
    template = 'web/user/global_blogs.html'
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


# FOR RESTAURANTS


def get_restaurant_promotions(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_promotions.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json_r, default=str),
            'restaurant': restaurant,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_foods(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_foods.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json, default=str),
            'restaurant': restaurant,
            'types': utils.FOOD_TYPE,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_drinks(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_drinks.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json, default=str),
            'restaurant': restaurant,
            'types': utils.DRINK_TYPE,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_dishes(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_dishes.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json, default=str),
            'restaurant': restaurant,
            'types': utils.DISH_TIME,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_menus_cuisine(request, branch, cuisine, slug):
    template = 'web/user/restaurant/get_restaurant_menus_cuisine.html'
    cuisine = RestaurantCategory.objects.get(pk=cuisine)
    branch = Branch.objects.get(pk=branch)
    foods = [food.menu for food in Food.objects.filter(branch__pk=branch.pk, cuisine__pk=cuisine.pk)]
    dishes = [dish.menu for dish in Dish.objects.filter(branch__pk=branch.pk, cuisine__pk=cuisine.pk)]
    menus = foods + dishes
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'cuisine': cuisine,
            'branch': branch,
            'menus': menus,
            'cuisines': sorted(branch.restaurant.categories, key=lambda c: random.random())[:4]
        })


def get_restaurant_menus_category(request, branch, category, slug):
    template = 'web/user/restaurant/get_restaurant_menus_category.html'
    category = FoodCategory.objects.get(pk=category)
    branch = Branch.objects.get(pk=branch)
    foods = [food.menu for food in Food.objects.filter(branch__pk=branch.pk, category__pk=category.pk)]
    dishes = [dish.menu for dish in Dish.objects.filter(branch__pk=branch.pk, category__pk=category.pk)]
    menus = foods + dishes
    categories = FoodCategory.objects.filter(restaurant__pk=branch.restaurant.pk).exclude(pk=category.pk).random(4)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'category': category,
            'branch': branch,
            'menus': menus,
            'categories': categories
        })


def get_restaurant_reviews(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_reviews.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json_r, default=str),
            'restaurant': restaurant,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_likes(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_likes.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json_r, default=str),
            'restaurant': restaurant,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


def get_restaurant_about(request, restaurant, branch, slug):
    template = 'web/user/restaurant/get_restaurant_about.html'
    restaurant = Branch.objects.get(pk=branch)
    menus = Menu.objects.filter(restaurant__pk=restaurant.pk)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'restaurant_json': json.dumps(restaurant.to_json_r, default=str),
            'restaurant': restaurant,
            'address_types': utils.USER_ADDRESS_TYPE,
            'table_locations': utils.TABLE_LOCATION
        })


@check_user_login(xhr='ajax')
def like_restaurant(request, restaurant, branch):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        restaurant = request.POST.get('restaurant')

        check = UserRestaurant.objects.filter(user__pk=user.pk, branch__pk=branch, restaurant__pk=restaurant)

        if check.count() > 0:
            check.delete()
            return HttpJsonResponse(ResponseObject('success', 'Restaurant Disliked !!!', 200))
        else:
            like = UserRestaurant(
                    user=User.objects.get(pk=user.pk),
                    restaurant=Restaurant.objects.get(pk=restaurant),
                    branch=Branch.objects.get(pk=branch)
                )
            like.save()
            return HttpJsonResponse(ResponseObject('success', 'Restaurant Liked !!!', 200))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def get_restaurant_map_pin_html(request, restaurant):
    template = 'web/user/restaurant/map_pin_html.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    return render(request, template, {'restaurant':restaurant})


def get_restaurant_map_pin_svg(request, restaurant, create=True):
    template = 'web/user/restaurant/map_pin_svg.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    
    logo = restaurant.logo.url
    data = logo.split('/')
    last = data[len(data) - 1]
    filename = '%s.svg' % last.split('.')[0]
    
    f = open(os.path.join(settings.MEDIA_ROOT, 'restaurants', 'pins', filename), 'w+')
    f.write(
            """<?xml version="1.0" encoding="utf-8"?>
                <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <path stroke-width="2" stroke-miterlimit="10" stroke="#b56fe8" fill="#b56fe8" d="M55.9 28.3c.1-.8.1-1.5.1-2.3a24 24 0 0 0-48 0c0 .8 0 1.6.1 2.3v.3C10.1 47.6 32 61 32 61s21.9-13.6 23.8-32.3z" data-name="layer2" stroke-linejoin="round" stroke-linecap="round"></path>
                    <defs>
                        <pattern id="image" x="0" y="0" patternUnits="userSpaceOnUse" height="64" width="64">
                            <image height="40" width="40" x="12" y="6" xlink:href="%s"></image>
                        </pattern>
                    </defs>
                    <circle stroke-width="2" stroke-miterlimit="10" stroke="#b56fe8" fill="url(#image)" r="17" cy="26" cx="32" data-name="layer1" stroke-linejoin="round" stroke-linecap="round"></circle>
                </svg>
            """ % restaurant.get_cover_base64()
        )
    f.close()
    if create == True:
        return render(request, template, {'restaurant':restaurant})


def get_restaurant_map_pin_img(request, restaurant):
    restaurant = Restaurant.objects.get(pk=restaurant)

    options = {
        'format': 'png',
        'crop-h': '53',
        'crop-w': '45',
        'crop-x': '8',
        'crop-y': '8',
        'encoding': "UTF-8",
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ]
    }

    config = imgkit.config(wkhtmltoimage='C:\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
    image = imgkit.from_url('{0}{1}'.format(utils.HOST_END_POINT, 
                                        reverse('ting_usr_restaurant_get_map_pin_html', kwargs={'restaurant':restaurant.pk})), 
                                                '%s.png' % restaurant.name.replace(' ', '-').lower(), config=config, options=options)

    return HttpResponse(image)


def load_branch_top_five(request, restaurant, branch):
    template = 'web/user/restaurant/load_ajax_branch_top_five.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    branch = Branch.objects.get(pk=branch)
    tops = Menu.objects.filter(restaurant__pk=restaurant.pk, branch__pk=branch.pk)[:5]
    return render(request, template, {'restaurant':restaurant, 'branch':branch, 'menus':tops})


def load_branch_menus_rand(request, branch):
    template = 'web/user/menu/load_branch_menus_rand.html'
    rand = request.GET.get('type')
    branch = Branch.objects.get(pk=branch)
    if rand == 'cat':
        categories = FoodCategory.objects.filter(restaurant__pk=branch.restaurant.pk).random(4)
        return render(request, template, {'categories': categories, 'type': rand, 'branch': branch})
    else:
        types = {'food': 1, 'drink': 2, 'dish': 3}
        menus = Menu.objects.filter(branch__pk=branch.pk, restaurant__pk=branch.restaurant.pk, menu_type=types[rand]).random(4)
        return render(request, template, {'menus': menus, 'type': rand, 'branch': branch})



def load_branch_directions(request, restaurant, branch):
    template = 'web/user/restaurant/load_branch_directions.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    branch = Branch.objects.get(pk=branch)
    location = {'latitude': request.GET.get('lat'), 'longitude': request.GET.get('long'), 'address': request.GET.get('addr'), 'country': request.GET.get('count'), 'town': request.GET.get('town')}
    return render(request, template, {
            'restaurant': restaurant, 
            'branch': json.dumps(branch.to_json_r, default=str),
            'location': json.dumps(location, default=str),
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
        })


@check_user_login(xhr='ajax')
def add_restaurant_review(request, restaurant, branch):

    check = RestaurantReview.objects.filter(branch__pk=branch, restaurant__pk=restaurant, user__pk=request.session['user'])

    if request.method == 'POST':
        review = RestaurantReviewForm(request.POST, instance=RestaurantReview(
                user=User.objects.get(pk=request.session['user']),
                branch=Branch.objects.get(pk=branch),
                restaurant=Restaurant.objects.get(pk=restaurant)
            ))
        if review.is_valid():
            
            if check.count() > 0:
                user_review = check.first()
                user_review.review = review.cleaned_data['review']
                user_review.comment = review.cleaned_data['comment']
                user_review.updated_at = timezone.now()
                user_review.save()
                return HttpJsonResponse(ResponseObject('success', 'Restaurant Reviewed !!!', 200))
            else:
                review.save()
                return HttpJsonResponse(ResponseObject('success', 'Restaurant Reviewed !!!', 200))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=review.errors.items()))
    else:
        return HttpResponse(
            json.dumps({"type": True, "data": {"review": check[0].review, "comment": check[0].comment}}, default=str)) if check.count() > 0 else HttpResponse(
                json.dumps({"type": False}))


def load_restaurant_reviews(request, restaurant, branch):
    template = 'web/user/restaurant/load_restaurant_reviews.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    branch = Branch.objects.get(pk=branch)
    reviews = RestaurantReview.objects.filter(branch__pk=branch.pk, restaurant__pk=restaurant.pk)
    return render(request, template, {
            'branch': branch,
            'restaurant': restaurant,
            'reviews': reviews
        })


def load_restaurant_likes(request, restaurant, branch):
    template = 'web/user/restaurant/load_restaurant_likes.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    branch = Branch.objects.get(pk=branch)
    likes = UserRestaurant.objects.filter(branch__pk=branch.pk, restaurant__pk=restaurant.pk)
    return render(request, template, {
            'branch': branch,
            'restaurant': restaurant,
            'likes': likes
        })


# FOR MENUS


@check_user_login(xhr='ajax')
def like_menu(request, menu):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        menu = request.POST.get('menu')

        check = MenuLike.objects.filter(user__pk=user.pk, menu__pk=menu)

        if check.count() > 0:
            check.delete()
            return HttpJsonResponse(ResponseObject('success', 'Restaurant Disliked !!!', 200))
        else:
            like = MenuLike(
                    user=User.objects.get(pk=user.pk),
                    menu=Menu.objects.get(pk=menu)
                )
            like.save()
            return HttpJsonResponse(ResponseObject('success', 'Restaurant Liked !!!', 200))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def interest_promotion(request, promo):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        promo = request.POST.get('promo')

        check = PromotionInterest.objects.filter(user__pk=user.pk, promotion__pk=promo)

        if check.count() > 0:
            check.delete()
            return HttpJsonResponse(ResponseObject('success', 'Not Interested In Promotion !!!', 200))
        else:
            like = PromotionInterest(
                    user=User.objects.get(pk=user.pk),
                    promotion=Promotion.objects.get(pk=promo)
                )
            like.save()
            return HttpJsonResponse(ResponseObject('success', 'Interested In Promotion !!!', 200))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


def get_menu(request, menu, slug):
    template = 'web/user/menu/get_menu.html'
    menu = Menu.objects.get(pk=menu)
    menu_dic = menu.to_json_f
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'menu_json': json.dumps(menu_dic, default=str),
            'menu': menu_dic,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


def get_promotion(request, promotion, slug):
    template = 'web/user/menu/get_promotion.html'
    promotion = Promotion.objects.get(pk=promotion)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json, default=str)  if 'user' in request.session else {},
            'promotion_json': json.dumps(promotion.to_json_b, default=str),
            'promotion': promotion.to_json_b,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


@check_user_login(xhr='ajax')
def add_menu_review(request, menu):

    check = MenuReview.objects.filter(menu__pk=menu, user__pk=request.session['user'])

    if request.method == 'POST':
        review = MenuReviewForm(request.POST, instance=MenuReview(
                menu=Menu.objects.get(pk=menu),
                user=User.objects.get(pk=request.session['user'])
            ))
        if review.is_valid():
            
            if check.count() > 0:
                user_review = check.first()
                user_review.review = review.cleaned_data['review']
                user_review.comment = review.cleaned_data['comment']
                user_review.updated_at = timezone.now()
                user_review.save()
                return HttpJsonResponse(ResponseObject('success', 'Menu Review Updated !!!', 200))
            else:
                review.save()
                return HttpJsonResponse(ResponseObject('success', 'Menu Reviewed !!!', 200))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=review.errors.items()))
    else:
        return HttpResponse(
            json.dumps({"type": True, "data": {"review": check[0].review, "comment": check[0].comment}}, default=str)) if check.count() > 0 else HttpResponse(
                json.dumps({"type": False}))


def load_menu_reviews(request, menu):
    template = 'web/user/menu/load_menu_reviews.html'
    reviews = MenuReview.objects.filter(menu__pk=menu).order_by('-updated_at')
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'reviews': reviews
        })


def load_menu_today_promotion(request, menu):
    template = 'web/user/menu/load_menu_today_promotion.html'
    menu = Menu.objects.get(pk=menu)
    promotions = Promotion.objects.filter(restaurant__pk=menu.restaurant.pk, branch__pk=menu.branch.pk)
    today_promos = list(filter(lambda promo: promo.is_on_today == True, promotions))
    today_type = list(filter(lambda promo: int(promo.promotion_menu_type) == 0 or int(promo.promotion_menu_type) == menu.menu_type, today_promos))
    promos_category = list(filter(lambda promo: int(promo.promotion_menu_type) == 5, today_promos))
    
    if menu.menu_type == 1:
        today_category = list(filter(lambda promo: promo.category.pk == menu.food.category.pk, promos_category))
    elif menu.menu_type == 3:
        today_category = list(filter(lambda promo: promo.category.pk == menu.dish.category.pk, promos_category))
    else:
        today_category = []

    promos_menu = list(filter(lambda promo: int(promo.promotion_menu_type) == 4, today_promos))
    today_menu = list(filter(lambda promo: promo.menu.pk == menu.pk, promos_menu))

    today_menu_promotions = today_type + today_category + today_menu
    promotion = random.choice(today_menu_promotions) if len(today_menu_promotions) > 0 else None
    return render(request, template,{'promotion': promotion, 'menu': menu})


# SEARCH


@require_http_methods(['GET'])
def live_search_response(request):
    
    query = request.GET.get('query')
    country = request.GET.get('country')
    town = request.GET.get('town')

    try:
        queries = query.split() if query != None else []
        queryset = reduce(operator.or_, [Q(name__icontains=q) for q in queries])
        branch_queryset = reduce(operator.or_, [Q(restaurant__name__icontains=q) | Q(name__icontains=q) | Q(tags__icontains=q) for q in queries])

        branches = list(map(lambda branch: branch.json_search(queries), Branch.objects.filter(country=country, town=town).filter(branch_queryset).order_by('-created_at')))
        foods = list(map(lambda food: food.json_search(queries), Food.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at')))
        drinks = list(map(lambda drink: drink.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at')))
        dishes = list(map(lambda dish: dish.json_search(queries), Drink.objects.filter(branch__country=country, branch__town=town).filter(queryset).order_by('-created_at')))

        results = branches + foods + drinks + dishes
        response = sorted(results, key=lambda res: res['qp'], reverse=True)
        return HttpResponse(json.dumps(response[:20], default=str), content_type='application/json')
    except Exception:
        return HttpResponse(json.dumps([], default=str), content_type='application/json')