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
                                Restaurant, User, UserResetPassword, UserAddress, Branch, UserRestaurant, Menu
                            )
from tingweb.forms import (
                                GoogleSignUpForm, UserLocationForm, EmailSignUpForm, UserImageForm
                            )
import ting.utils as utils
from datetime import datetime, timedelta
import json
import imgkit
import os


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


def index(request):
	template = 'web/index.html'
	return render(request, template, {
            'address_types': utils.USER_ADDRESS_TYPE,
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None
        })


# USER LOGIN, SIGNUP & PROFILE


@csrf_exempt
def sign_up_with_google(request):
    if request.method == 'POST':
        user_form = GoogleSignUpForm(request.POST, instance=User(
                image=utils.DEFAULT_USER_IMAGE,
                username=request.POST.get('name').replace(' ', '_').lower(),
                phone=''
            ))
        token = request.POST.get('token')
        email = request.POST.get('email')

        token_id = token.split('-')[0]
        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_index')

        try:
            check_user = User.objects.get(email=email)
            if 'user' in request.session:
                if request.session['user'] == check_user.pk:
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link))
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
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link))
                else:
                    check_user.token = token
                    check_user.updated_at = timezone.now()
                    check_user.save()
                    request.session['user'] = check_user.pk
                    
                    messages.success(request, 'User Logged In Successfully !!!')
                    return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link))

        except User.DoesNotExist:
            address_form = UserLocationForm(request.POST)

            if address_form.is_valid() and user_form.is_valid():
                user = user_form.save()
                address = address_form.save(commit=False)
                address.user = User.objects.get(pk=user.pk)
                address.save()
                request.session['user'] = user.pk
                
                messages.success(request, 'User Signed In Successfully !!!')
                return HttpJsonResponse(ResponseObject('success', 'User Signed In Successfully !!!', 200, link))
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
                phone=''
            ))

        link = request.POST.get('link') if request.POST.get('link') != '' else reverse('ting_index')
        address_form = UserLocationForm(request.POST)

        if request.POST.get('type').lower() == 'other' and (request.POST.get('other_address_type') == None or request.POST.get() == ''):
            return HttpJsonResponse(ResponseObject('error', 'You Selected Address As Other. Please, Enter The Other Type Of Address !!!', 406))

        try:
            bd = datetime.strptime(request.POST.get('date_of_birth'), '%Y-%m-%d')
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
            
            messages.success(request, 'User Registered Successfully !!!')
            return HttpJsonResponse(ResponseObject('success', 'User Registered Successfully !!!', 200, link))
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
            return HttpJsonResponse(ResponseObject('success', 'User Logged In Successfully !!!', 200, link))
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

            return HttpJsonResponse(ResponseObject('success', 'Reset Password Link Mail Sent Successfully !!!', 400))

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
    template = 'web/user/user_profile.html'
    user = get_object_or_404(User, pk=user)
    
    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))
    
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
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
            return HttpJsonResponse(ResponseObject('success', 'User Image Updated Successfully !!!', 200))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Insert A Valid Image !!!', 400, msgs=form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def update_user_password(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        conf_password = request.POST.get('confirm_password')

        if check_password(user.password, old_password) == True or old_password == None:
            if conf_password == new_password:
                user.password = make_password(conf_password)
                user.updated_at = timezone.now()
                user.save()

                return HttpJsonResponse(ResponseObject('success', 'User Password Updated Successfully !!!', 200))
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

                    mail = SendUserUpdateEmailMail(email=email, context={
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

                    return HttpJsonResponse(ResponseObject('success', 'User Email Updated Successfully !!!', 200))
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
            return HttpJsonResponse(ResponseObject('success', 'Address Added Successfully !!!', 200, link))
        else:
            return HttpJsonResponse(ResponseObject('error', 'Fill All Fields With Right Data !!!', 406, 
                    msgs=address_form.errors.items()))
    else:
        return HttpJsonResponse(ResponseObject('error', 'Method Not Allowed', 405))


@check_user_login(xhr='ajax')
def load_user_edit_address(request, address):
    template = 'web/user/ajax/load_user_edit_address.html'
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
            return HttpJsonResponse(ResponseObject('success', 'Address Updated Successfully !!!', 200, link))
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
        return HttpJsonResponse(ResponseObject('success', 'Address Deleted Successfully !!!', 403, 
                reverse('ting_usr_profile', kwargs={'user':user.pk, 'username':user.username})))
    else:
        messages.error(request, 'You Need At Least 1 Address !!!')
        return HttpJsonResponse(ResponseObject('error', 'You Need At Least 1 Address !!!', 403, 
                reverse('ting_usr_profile', kwargs={'user':user.pk, 'username':user.username})))


def user_moments(request, user, username):
    template = 'web/user/user_moments.html'
    user = get_object_or_404(User, pk=user)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


def user_restaurants(request, user, username):
    template = 'web/user/user_restaurants.html'
    user = get_object_or_404(User, pk=user)
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'user': user,
            'address_types': utils.USER_ADDRESS_TYPE,
        })


@check_user_login(xhr='GET')
def user_orders(request, user, username):
    template = 'web/user/user_orders.html'
    user = get_object_or_404(User, pk=user)

    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'user': user
        })


@check_user_login(xhr='GET')
def user_bookings(request, user, username):
    template = 'web/user/user_bookings.html'
    user = get_object_or_404(User, pk=user)

    if user.pk != request.session['user']:
        session = User.objects.get(pk=request.session['user'])
        return HttpResponseRedirect(reverse('ting_usr_profile', kwargs={'user':session.pk, 'username':session.username}))

    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'user': user
        })


# GLOBAL LINKS


def discovery(request):
    template = 'web/user/global_discovery.html'
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
        })

def restaurants(request):
    template = 'web/user/global_restaurants.html'
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
            'session_json': json.dumps(User.objects.get(pk=request.session['user']).to_json(), default=str)  if 'user' in request.session else {},
            'branches': json.dumps([branch.to_json_r() for branch in Branch.objects.all()], default=str),
            'countries': json.dumps(list(Branch.objects.values('country').annotate(branches=Count('country'))), default=str),
            'towns': json.dumps(list(Branch.objects.values('town', 'country').annotate(branches=Count('town'))), default=str),
        })

def moments(request):
    template = 'web/user/global_moments.html'
    return render(request, template, {
            'is_logged_in': True if 'user' in request.session else False,
            'session': User.objects.get(pk=request.session['user']) if 'user' in request.session else None,
            'address_types': utils.USER_ADDRESS_TYPE,
        })



# FOR RESTAURANTS


def filter_restaurants_search(request):
    resto = request.POST.get('resto') if request.POST.get('resto') != None else ''
    branch = request.POST.get('branch') if request.POST.get('branch') != None else ''
    country = request.POST.get('country')

    branches = Branch.objects.filter(
                restaurant__name__icontains=resto, 
                name__icontains=branch, 
                country=country) if country != 'all' else Branch.objects.filter(
                    restaurant__name__icontains=resto, 
                    name__icontains=branch)

    return HttpJsonResponse([branch.to_json_r() for branch in branches])


@check_user_login(xhr='ajax')
def like_restaurant(request, restaurant):
    if request.method == 'POST':
        user = User.objects.get(pk=request.session['user'])
        restaurant = request.POST.get('restaurant')

        check = UserRestaurant.objects.filter(user__pk=user.pk, restaurant__pk=restaurant)

        if check.count() > 0:
            check.delete()
            return HttpJsonResponse(ResponseObject('success', 'Restaurant Disliked !!!', 200))
        else:
            like = UserRestaurant(
                    user=User.objects.get(pk=user.pk),
                    restaurant=Restaurant.objects.get(pk=restaurant)
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
            """
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

    image = imgkit.from_url('{0}{1}'.format('http://localhost:8000', 
                                        reverse('ting_usr_restaurant_get_map_pin_html', kwargs={'restaurant':restaurant.pk})), 
                                                '%s.png' % restaurant.name.replace(' ', '-').lower(), config=config, options=options)

    return HttpResponse(image)


def load_branch_top_five(request, restaurant, branch):
    template = 'web/user/restaurant/load_ajax_branch_top_five.html'
    restaurant = Restaurant.objects.get(pk=restaurant)
    branch = Branch.objects.get(pk=branch)

    tops = Menu.objects.filter(restaurant__pk=restaurant.pk, branch__pk=branch.pk)[:5]

    return render(request, template, {'restaurant':restaurant, 'branch':branch, 'menus':tops})