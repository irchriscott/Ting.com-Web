# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.context_processors import csrf
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse, request
from django.urls import reverse
from django.contrib import messages
from ting.responses import ResponseObject, HttpJsonResponse
from tingweb.models import Restaurant
import ting.utils as utils
import datetime


# Create your views here.


def check_user_login(func):
    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session.keys():
            messages.error(request, 'Login Required, Please !!!')
            return HttpResponseRedirect(reverse('ting_index'))
        return func(request, *args, **kwargs)
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def index(request):
	template = 'web/index.html'
	return render(request, template, {})
