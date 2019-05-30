# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from time import time

# Create your models here.

def package_image_path(instance, filename):
	return "packages/%s_%s" % (str(time()).replace('.','_'), filename)

class TingPackage(models.Model):
	name = models.CharField(max_length=200, null=False, blank=False)
	image = models.ImageField(upload_to=package_image_path, null=False, blank=False)
	tables = models.IntegerField(null=False, blank=False)
	menus = models.IntegerField(null=False, blank=False)
	amount = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	currency = models.CharField(max_length=100, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name


class TingLicenceKey(models.Model):
	admin = models.ForeignKey(User)
	package = models.ForeignKey(TingPackage)
	key = models.CharField(max_length=24, null=False, blank=False)
	duration = models.IntegerField(null=False, blank=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.key

	def __unicode__(self):
		return self.key

	@property
	def licence_key(self):
		key = list(self.key)
		key.insert(4, '-')
		key.insert(9, '-')
		key.insert(14, '-')
		key.insert(19, '-')
		return "".join(key)


class RestaurantCategory(models.Model):
	name = models.CharField(max_length=200, null=False, blank=True)
	country = models.CharField(max_length=200, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	def to_json(self):
		return {
			'name': self.name,
			'country': self.country,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Permission(models.Model):
	title = models.CharField(max_length=200, null=False, blank=False)
	category = models.CharField(max_length=200, null=False, blank=False)
	permission = models.CharField(max_length=200, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.permission

	def __unicode__(self):
		return self.permission

	def to_json(self):
		return {
			'id': self.pk,
			'title': self.title,
			'category': self.category,
			'permission': self.permission,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}
