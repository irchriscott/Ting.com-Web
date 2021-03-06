# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from django_random_queryset import RandomManager
from django.contrib.humanize.templatetags.humanize import intcomma
from tingadmin.models import RestaurantCategory, TingLicenceKey, Permission
from datetime import date, datetime
from time import time
import ting.utils as utils
import random
import os

# Create your models here.

def restaurant_logo_path(instance, filename):
	return "restaurants/logos/%s_%s" % (str(time()).replace('.','_'), filename)

def restaurant_image_path(instance, filename):
	return "restaurants/images/%s_%s" % (str(time()).replace('.','_'), filename)

def administrator_image_path(instance, filename):
	return "administrators/%s_%s" % (str(time()).replace('.','_'), filename)

def user_image_path(instance, filename):
	return "users/%s_%s" % (str(time()).replace('.','_'), filename)

def food_image_path(instance, filename):
	return "menus/%s_%s" % (str(time()).replace('.','_'), filename)

def category_image_path(instance, filename):
	return "categories/%s_%s" % (str(time()).replace('.','_'), filename)

def promotion_image_path(instance, filename):
	return "promotions/%s_%s" % (str(time()).replace('.','_'), filename)

def moment_file_path(instance, filename):
	return "moments/%s_%s" % (str(time()).replace('.','_'), filename)

def get_menu_name(value):
	menu = Menu.objects.get(pk=value)
	if menu.menu_type == 1:
		food = Food.objects.get(pk=menu.menu_id)
		return food.name
	elif menu.menu_type == 2:
		drink = Drink.objects.get(pk=menu.menu_id)
		return drink.name
	elif menu.menu_type == 3:
		dish = Dish.objects.get(pk=menu.menu_id)
		return dish.name


def get_menu_image(value):
	menu = Menu.objects.get(pk=value)
	if menu.menu_type == 1:
		food = Food.objects.get(pk=menu.menu_id)
		return food.images[0].image.url
	elif menu.menu_type == 2:
		drink = Drink.objects.get(pk=menu.menu_id)
		return drink.images[0].image.url
	elif menu.menu_type == 3:
		dish = Dish.objects.get(pk=menu.menu_id)
		return dish.images[0].image.url


def get_menu_type(value):
	menu = Menu.objects.get(pk=value)
	if menu.menu_type == 1:
		food = Food.objects.get(pk=menu.menu_id)
		return '%s, %s' % ('Food', utils.get_from_tuple(utils.FOOD_TYPE, food.food_type))
	elif menu.menu_type == 2:
		drink = Drink.objects.get(pk=menu.menu_id)
		return '%s, %s' % ('Drink', utils.get_from_tuple(utils.DRINK_TYPE, drink.drink_type))
	elif menu.menu_type == 3:
		dish = Dish.objects.get(pk=menu.menu_id)
		return '%s, %s' % ('Drink', utils.get_from_tuple(utils.DISH_TIME, dish.dish_time))


### USER RESTAURANT


class Restaurant(models.Model):
	token = models.TextField(null=False, blank=False)
	name = models.CharField(max_length=200, null=False, blank=False)
	motto = models.TextField(null=True, blank=True)
	purpose = models.IntegerField(null=False, blank=False, default=2)
	slug = models.CharField(max_length=255, null=False, blank=False)
	logo = models.ImageField(upload_to=restaurant_logo_path, null=False, blank=False)
	country = models.CharField(max_length=200, null=False, blank=False)
	town = models.CharField(max_length=255, null=False, blank=False)
	opening = models.TimeField(null=False, blank=False)
	closing = models.TimeField(null=False, blank=False)
	is_authenticated = models.BooleanField(default=False)
	is_disabled = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def uuid(self):
		arr = self.slug.split('-')
		return arr[len(arr) - 1]

	@property
	def opening_str(self):
		return self.opening.strftime('%H:%M')

	@property
	def closing_str(self):
		return self.closing.strftime('%H:%M')

	@property
	def purpose_str(self):
		return utils.get_from_tuple(utils.ACCOUNT_PURPOSE, self.purpose)

	@property
	def name_hi(self):
		return self.name.replace(' ', '-').lower()
	
	@property
	def categories(self):
		return CategoryRestaurant.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def categories_ids(self):
		return [category.category.id for category in self.categories]
	
	def has_category(self, c):
		return True if c in self.categories_ids else False

	@property
	def tables(self):
		return RestaurantTable.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def tables_count(self):
		return self.tables.count()

	@property
	def administrators(self):
		return Administrator.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def administrators_count(self):
		return self.administrators.count()

	@property
	def config(self):
		return RestaurantConfig.objects.filter(restaurant=self.pk).first()

	@property
	def likes(self):
		return UserRestaurant.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def likes_count(self):
		return self.likes.count()

	@property
	def reviews(self):
		return RestaurantReview.objects.filter(restaurant=self.pk).order_by('created_at')

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def food_categories(self):
		return FoodCategory.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def food_categories_count(self):
		return self.food_categories.count()

	@property
	def menus(self):
		return Menu.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def menus_count(self):
		return self.menus.count()

	@property
	def foods(self):
		return Food.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def foods_count(self):
		return self.foods.count()

	@property
	def appetizers(self):
		return Food.objects.filter(restaurant=self.pk, food_type=1).order_by('-created_at')

	@property
	def appetizers_count(self):
		return self.appetizers.count()

	@property
	def meals(self):
		return Food.objects.filter(restaurant=self.pk, food_type=2).order_by('-created_at')

	@property
	def meals_count(self):
		return self.meals.count()

	@property
	def desserts(self):
		return Food.objects.filter(restaurant=self.pk, food_type=3).order_by('-created_at')

	@property
	def desserts_count(self):
		return self.desserts.count()

	@property
	def sauces(self):
		return Food.objects.filter(restaurant=self.pk, food_type=4).order_by('-created_at')

	@property
	def sauces_count(self):
		return self.sauces.count()

	@property
	def drinks(self):
		return Drink.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def drinks_count(self):
		return self.drinks.count()

	@property
	def dishes(self):
		return Dish.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def dishes_count(self):
		return self.dishes.count()

	@property
	def images(self):
		return RestaurantImage.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def branches(self):
		return Branch.objects.filter(restaurant=self.pk).order_by('created_at')

	@property
	def branches_count(self):
		return self.branches.count()

	@property
	def map_ping_svg_name(self):
		namedata = self.logo.url.split('/')
		name = namedata[len(namedata) - 1]
		svgname = '%s.svg' % name.split('.')[0]
		return svgname

	@property
	def map_pin_svg(self):
		return '/tinguploads/restaurants/pins/' + self.map_ping_svg_name
	
	def get_cover_base64(self):
		return utils.image_as_base64(self.logo.path)

	@property
	def get_pin_base64(self):
		return utils.image_as_base64(self.map_pin_svg).replace('data:image/png;base64,', '')

	@property
	def get_pin_string(self):
		file = open('tinguploads/restaurants/pins/' + self.map_ping_svg_name, 'r')
		return file.read()

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'motto': self.motto,
			'purposeId': self.purpose,
			'purpose': self.purpose_str,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.category.to_json for category in self.categories]
			},
			'logo': self.logo.url,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'country': self.country,
			'town': self.town,
			'opening': self.opening.strftime('%H:%M'),
			'closing': self.closing.strftime('%H:%M'),
			'menus': {
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				}
			},
			'branches': {
				'count': self.branches.count()
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'tables': {
				'count': self.tables_count,
				'tables': [table.to_json_s for table in self.tables]
			},
			'likes':{
				'count': self.likes_count,
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json for category in self.food_categories]
			},
			'config': self.config.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_u(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'motto': self.motto,
			'purposeId': self.purpose,
			'purpose': self.purpose_str,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.category.to_json for category in self.categories]
			},
			'logo': self.logo.url,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'country': self.country,
			'town': self.town,
			'opening': self.opening.strftime('%H:%M'),
			'closing': self.closing.strftime('%H:%M'),
			'menus': {
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				}
			},
			'branches': {
				'count': self.branches.count()
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'tables': {
				'count': self.tables_count,
				'tables': [table.to_json_s for table in self.tables]
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json for category in self.food_categories]
			},
			'config': self.config.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_b(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'motto': self.motto,
			'purposeId': self.purpose,
			'purpose': self.purpose_str,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.category.to_json for category in self.categories]
			},
			'logo': self.logo.url,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'country': self.country,
			'town': self.town,
			'opening': self.opening.strftime('%H:%M'),
			'closing': self.closing.strftime('%H:%M'),
			'menus': {
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				}
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json for category in self.food_categories]
			},
			'config': self.config.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'motto': self.motto,
			'purposeId': self.purpose,
			'purpose': self.purpose_str,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.category.to_json for category in self.categories]
			},
			'logo': self.logo.url,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'country': self.country,
			'town': self.town,
			'opening': self.opening.strftime('%H:%M'),
			'closing': self.closing.strftime('%H:%M'),
			'branches': {
				'count': self.branches.count()
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'tables': {
				'count': self.tables_count
			},
			'likes':{
				'count': self.likes_count
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json for category in self.food_categories]
			},
			'config': self.config.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'motto': self.motto,
			'purposeId': self.purpose,
			'purpose': self.purpose_str,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.category.to_json for category in self.categories]
			},
			'logo': self.logo.url,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'country': self.country,
			'town': self.town,
			'opening': self.opening.strftime('%H:%M'),
			'closing': self.closing.strftime('%H:%M'),
			'branches': {
				'count': self.branches.count()
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'tables': {
				'count': self.tables_count
			},
			'likes':{
				'count': self.likes_count
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json for category in self.food_categories]
			},
			'config': self.config.to_json_admin,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Branch(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	name = models.CharField(max_length=200, null=False, blank=False)
	country = models.CharField(max_length=200, null=False, blank=False)
	town = models.CharField(max_length=255, null=False, blank=False)
	region = models.CharField(max_length=255, null=True, blank=True)
	road = models.CharField(max_length=255, null=True, blank=True)
	address = models.TextField(null=False, blank=False)
	latitude = models.CharField(max_length=200, null=False, blank=False)
	longitude = models.CharField(max_length=200, null=False, blank=False)
	place_id = models.CharField(max_length=200, null=False, blank=False)
	email = models.EmailField(null=True, blank=True)
	phone = models.CharField(max_length=255, null=True, blank=True)
	channel = models.CharField(max_length=255, null=True, blank=True)
	specials = models.CharField(max_length=255, null=True, blank=True)
	services = models.CharField(max_length=255, null=True, blank=True)
	tags = models.CharField(max_length=255, null=True, blank=True)
	restaurant_type = models.IntegerField(null=False, blank=True, default=1)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def name_hi(self):
		return self.name.replace(' ', '-').lower()

	@property
	def full_name(self):
		return '%s, %s' % (self.restaurant.name, self.name)

	@property
	def is_opened(self):
		now = datetime.strptime('1970-01-01 {0}'.format(datetime.strftime(datetime.now(), '%H:%M')), '%Y-%m-%d %H:%M')
		opening = datetime.strptime('1970-01-01 {0}'.format(self.restaurant.opening_str), '%Y-%m-%d %H:%M')
		closing = datetime.strptime('1970-01-01 {0}'.format(self.restaurant.closing_str), '%Y-%m-%d %H:%M')
		return True if now >= opening and closing > now else False

	@property
	def availability(self):
		if self.is_available:
			return 2 if self.is_opened else 3
		else:
			return 1

	@property
	def restaurant_type_str(self):
		return utils.get_from_dict(utils.RESTAURANT_TYPES, 'id', int(self.restaurant_type))
	
	@property
	def likes(self):
		return UserRestaurant.objects.filter(restaurant=self.restaurant.pk, branch=self.pk).order_by('-created_at')

	@property
	def likes_ids(self):
		return [like.user.pk for like in self.likes]

	def has_liked(self, u):
		return True if u in self.likes_ids else False
	
	@property
	def likes_count(self):
		return self.likes.count()

	@property
	def reviews(self):
		return RestaurantReview.objects.filter(restaurant=self.restaurant.pk, branch=self.pk).order_by('created_at')

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def tables(self):
		return RestaurantTable.objects.filter(branch=self.pk)

	@property
	def tables_count(self):
		return self.tables.count()

	@property
	def available_table_location(self):
		tables = []
		if self.tables.filter(location=1).count() > 0:
			tables.append(1)
		if self.tables.filter(location=2).count() > 0:
			tables.append(2)
		if self.tables.filter(location=3).count() > 0:
			tables.append(3)
		if self.tables.filter(location=4).count() > 0:
			tables.append(4)
		return tables

	@property
	def menus(self):
		return Menu.objects.filter(branch=self.pk)

	@property
	def menus_count(self):
		return self.menus.count()

	@property
	def foods(self):
		return Food.objects.filter(branch=self.pk).order_by('-created_at')

	@property
	def foods_count(self):
		return self.foods.count()

	@property
	def appetizers(self):
		return Food.objects.filter(branch=self.pk, food_type=1).order_by('-created_at')

	@property
	def appetizers_count(self):
		return self.appetizers.count()

	@property
	def meals(self):
		return Food.objects.filter(branch=self.pk, food_type=2).order_by('-created_at')

	@property
	def meals_count(self):
		return self.meals.count()

	@property
	def desserts(self):
		return Food.objects.filter(branch=self.pk, food_type=3).order_by('-created_at')

	@property
	def desserts_count(self):
		return self.desserts.count()

	@property
	def sauces(self):
		return Food.objects.filter(branch=self.pk, food_type=4).order_by('-created_at')

	@property
	def sauces_count(self):
		return self.sauces.count()

	@property
	def drinks(self):
		return Drink.objects.filter(branch=self.pk).order_by('-created_at')

	@property
	def drinks_count(self):
		return self.drinks.count()

	@property
	def dishes(self):
		return Dish.objects.filter(branch=self.pk).order_by('-created_at')

	@property
	def dishes_count(self):
		return self.dishes.count()

	@property
	def specials_ids(self):
		return self.specials.split(',') if self.specials != None else []

	def has_special(self, s):
		return True if str(s) in self.specials else False

	@property
	def get_specials(self):
		return [utils.get_from_dict(utils.RESTAURANT_SPECIALS, 'id', int(s)) for s in self.specials_ids]

	@property
	def services_ids(self):
		return self.services.split(',') if self.services != None else []
	
	def has_service(self, s):
		return True if str(s) in self.services else False

	@property
	def get_services(self):
		return [utils.get_from_dict(utils.RESTAURANT_SERVICES, 'id', int(s)) for s in self.services_ids]

	@property
	def get_tags(self):
		return self.tags.split(',') if self.tags != None and self.tags != '' else []
	
	@property
	def promotions(self):
		return Promotion.objects.filter(branch__pk=self.pk).order_by('-updated_at')
	
	@property
	def promotions_count(self):
		return self.promotions.count()

	@property
	def socket_data(self):
		return {
			'id': self.pk,
			'type': 1,
			'name': '%s, %s' % (self.restaurant.name, self.name),
			'email': self.email,
			'image': self.restaurant.logo.url,
			'channel': self.channel
		}
	
	@property
	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_b,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type_str,
			'specials': self.get_specials,
			'services': self.get_services,
			'tags': self.get_tags,
			'categories': {
				'count': self.restaurant.categories.count(),
				'categories': [category.category.to_json for category in self.restaurant.categories]
			},
			'tables':{
				'count': self.tables_count,
				'iron': self.tables.filter(chair_type=1).count(),
				'wooden': self.tables.filter(chair_type=2).count(),
				'plastic': self.tables.filter(chair_type=3).count(),
				'couch': self.tables.filter(chair_type=4).count(),
				'mixture': self.tables.filter(chair_type=5).count(),
				'inside': self.tables.filter(location=1).count(),
				'outside': self.tables.filter(location=2).count(),
				'balcony': self.tables.filter(location=3).count(),
				'rooftop': self.tables.filter(location=4).count(),
				'tables': [table.to_json_s for table in self.tables]
			},
			'menus':{
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				},
				'menus': [menu.to_json for menu in self.menus]
			},
			'promotions':{
				'count': self.promotions_count,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json_b for review in self.reviews[:5]]
			},
			'likes':{
				'count': self.likes_count,
				'likes': self.likes_ids
			},
			'urls':{
				'relative': reverse('ting_usr_get_restaurant_promotions', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk, 'slug': self.restaurant.slug}),
				'loadReviews': reverse('ting_usr_load_restaurant_reviews', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'addReview': reverse('ting_usr_add_restaurant_review', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'likeBranch': reverse('ting_usr_like_restaurant_toggle', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'loadLikes': reverse('ting_usr_load_restaurant_likes', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'apiGet': reverse('api_restaurant_get', kwargs={'branch': self.pk}),
				'apiPromotions': reverse('api_restaurant_promotions', kwargs={'branch': self.pk}),
				'apiFoods': reverse('api_restaurant_foods', kwargs={'branch': self.pk}),
				'apiDrinks': reverse('api_restaurant_drinks', kwargs={'branch': self.pk}),
				'apiDishes': reverse('api_restaurant_dishes', kwargs={'branch': self.pk}),
				'apiReviews': reverse('api_restaurant_reviews', kwargs={'branch': self.pk}),
				'apiAddReview': reverse('api_add_restaurant_review', kwargs={'branch': self.pk}),
				'apiLikes': reverse('api_restaurant_likes', kwargs={'branch': self.pk}),
				'apiAddLike': reverse('api_like_restaurant', kwargs={'branch': self.pk})
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_r(self):
		return {
			'id': self.pk,
			'name': self.name,
			'country': self.country,
			'restaurant': self.restaurant.to_json_b,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type_str,
			'specials': self.get_specials,
			'services': self.get_services,
			'tags': self.get_tags,
			'categories': {
				'count': self.restaurant.categories.count(),
				'categories': [category.category.to_json for category in self.restaurant.categories]
			},
			'tables':{
				'count': self.tables_count,
				'iron': self.tables.filter(chair_type=1).count(),
				'wooden': self.tables.filter(chair_type=2).count(),
				'plastic': self.tables.filter(chair_type=3).count(),
				'couch': self.tables.filter(chair_type=4).count(),
				'mixture': self.tables.filter(chair_type=5).count(),
				'inside': self.tables.filter(location=1).count(),
				'outside': self.tables.filter(location=2).count(),
				'balcony': self.tables.filter(location=3).count(),
				'rooftop': self.tables.filter(location=4).count(),
				'tables': [table.to_json_s for table in self.tables]
			},
			'menus':{
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				},
				'menus': [menu.to_json_s for menu in self.menus.random(4)]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json_b for review in self.reviews[:5]]
			},
			'likes':{
				'count': self.likes_count,
				'likes': self.likes_ids
			},
			'urls':{
				'relative': reverse('ting_usr_get_restaurant_promotions', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk, 'slug': self.restaurant.slug}),
				'loadReviews': reverse('ting_usr_load_restaurant_reviews', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'addReview': reverse('ting_usr_add_restaurant_review', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'likeBranch': reverse('ting_usr_like_restaurant_toggle', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'loadLikes': reverse('ting_usr_load_restaurant_likes', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'apiGet': reverse('api_restaurant_get', kwargs={'branch': self.pk}),
				'apiPromotions': reverse('api_restaurant_promotions', kwargs={'branch': self.pk}),
				'apiFoods': reverse('api_restaurant_foods', kwargs={'branch': self.pk}),
				'apiDrinks': reverse('api_restaurant_drinks', kwargs={'branch': self.pk}),
				'apiDishes': reverse('api_restaurant_dishes', kwargs={'branch': self.pk}),
				'apiReviews': reverse('api_restaurant_reviews', kwargs={'branch': self.pk}),
				'apiAddReview': reverse('api_add_restaurant_review', kwargs={'branch': self.pk}),
				'apiLikes': reverse('api_restaurant_likes', kwargs={'branch': self.pk}),
				'apiAddLike': reverse('api_like_restaurant', kwargs={'branch': self.pk})
			},
			'promotions':{
				'count': self.promotions_count,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_u(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_u,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type_str,
			'specials': self.get_specials,
			'services': self.get_services,
			'tags': self.get_tags,
			'categories': {
				'count': self.restaurant.categories.count(),
				'categories': [category.category.to_json for category in self.restaurant.categories]
			},
			'tables':{
				'count': self.tables_count,
				'iron': self.tables.filter(chair_type=1).count(),
				'wooden': self.tables.filter(chair_type=2).count(),
				'plastic': self.tables.filter(chair_type=3).count(),
				'couch': self.tables.filter(chair_type=4).count(),
				'mixture': self.tables.filter(chair_type=5).count(),
				'inside': self.tables.filter(location=1).count(),
				'outside': self.tables.filter(location=2).count(),
				'balcony': self.tables.filter(location=3).count(),
				'rooftop': self.tables.filter(location=4).count(),
				'tables': [table.to_json_s for table in self.tables]
			},
			'menus':{
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				}
			},
			'promotions':{
				'count': self.promotions_count
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes':{
				'count': self.likes_count,
				'likes': self.likes_ids
			},
			'urls':{
				'relative': reverse('ting_usr_get_restaurant_promotions', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk, 'slug': self.restaurant.slug}),
				'loadReviews': reverse('ting_usr_load_restaurant_reviews', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'addReview': reverse('ting_usr_add_restaurant_review', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'likeBranch': reverse('ting_usr_like_restaurant_toggle', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'loadLikes': reverse('ting_usr_load_restaurant_likes', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'apiGet': reverse('api_restaurant_get', kwargs={'branch': self.pk}),
				'apiPromotions': reverse('api_restaurant_promotions', kwargs={'branch': self.pk}),
				'apiFoods': reverse('api_restaurant_foods', kwargs={'branch': self.pk}),
				'apiDrinks': reverse('api_restaurant_drinks', kwargs={'branch': self.pk}),
				'apiDishes': reverse('api_restaurant_dishes', kwargs={'branch': self.pk}),
				'apiReviews': reverse('api_restaurant_reviews', kwargs={'branch': self.pk}),
				'apiAddReview': reverse('api_add_restaurant_review', kwargs={'branch': self.pk}),
				'apiLikes': reverse('api_restaurant_likes', kwargs={'branch': self.pk}),
				'apiAddLike': reverse('api_like_restaurant', kwargs={'branch': self.pk})
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type_str,
			'specials': self.get_specials,
			'services': self.get_services,
			'tags': self.get_tags,
			'categories': {
				'count': self.restaurant.categories.count(),
				'categories': [category.category.to_json for category in self.restaurant.categories]
			},
			'tables':{
				'count': self.tables_count,
				'iron': self.tables.filter(chair_type=1).count(),
				'wooden': self.tables.filter(chair_type=2).count(),
				'plastic': self.tables.filter(chair_type=3).count(),
				'couch': self.tables.filter(chair_type=4).count(),
				'mixture': self.tables.filter(chair_type=5).count(),
				'inside': self.tables.filter(location=1).count(),
				'outside': self.tables.filter(location=2).count(),
				'balcony': self.tables.filter(location=3).count(),
				'rooftop': self.tables.filter(location=4).count(),
			},
			'menus':{
				'count': self.menus_count,
				'type': {
					'foods':{
						'count': self.foods_count,
						'type': {
							'appetizers': self.appetizers_count,
							'meals': self.meals_count,
							'desserts': self.desserts_count,
							'sauces': self.sauces_count
						}
					},
					'drinks': self.drinks_count,
					'dishes': self.dishes_count
				}
			},
			'promotions':{
				'count': self.promotions_count
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes':{
				'count': self.likes_count,
				'likes': self.likes_ids
			},
			'urls':{
				'relative': reverse('ting_usr_get_restaurant_promotions', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk, 'slug': self.restaurant.slug}),
				'loadReviews': reverse('ting_usr_load_restaurant_reviews', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'addReview': reverse('ting_usr_add_restaurant_review', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'likeBranch': reverse('ting_usr_like_restaurant_toggle', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'loadLikes': reverse('ting_usr_load_restaurant_likes', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk}),
				'apiGet': reverse('api_restaurant_get', kwargs={'branch': self.pk}),
				'apiPromotions': reverse('api_restaurant_promotions', kwargs={'branch': self.pk}),
				'apiFoods': reverse('api_restaurant_foods', kwargs={'branch': self.pk}),
				'apiDrinks': reverse('api_restaurant_drinks', kwargs={'branch': self.pk}),
				'apiDishes': reverse('api_restaurant_dishes', kwargs={'branch': self.pk}),
				'apiReviews': reverse('api_restaurant_reviews', kwargs={'branch': self.pk}),
				'apiAddReview': reverse('api_add_restaurant_review', kwargs={'branch': self.pk}),
				'apiLikes': reverse('api_restaurant_likes', kwargs={'branch': self.pk}),
				'apiAddLike': reverse('api_like_restaurant', kwargs={'branch': self.pk})
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	
	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_admin,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type,
			'specials': self.get_specials,
			'services': self.get_services,
			'tags': self.get_tags,
			'categories': {
				'count': self.restaurant.categories.count(),
				'categories': [category.category.to_json for category in self.restaurant.categories]
			},
			'promotions':{
				'count': self.promotions_count
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes':{
				'count': self.likes_count
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_admin_s(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_admin,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'region': self.region,
			'road': self.road,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'email': self.email,
			'phone': self.phone,
			'channel': self.channel,
			'isAvailable': self.is_available,
			'type': self.restaurant_type,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	def json_search(self, queries):
		name = '%s, %s' % (self.restaurant.name, self.name)
		return  {
			'id': self.pk,
			'type': 1,
			'image': self.restaurant.logo.url,
			'name': name,
			'description': self.address,
			'tags': self.get_tags,
			'text': ', '.join(map(lambda c: c.category.name, self.restaurant.categories)),
			'reviews': self.reviews_count,
			'reviewAverage': self.review_average,
			'qp': utils.query_priority(name, queries),
			'coords': {'lat': self.latitude, 'lng': self.longitude},
			'apiGet': reverse('api_restaurant_get', kwargs={'branch': self.pk}),
			'relative': reverse('ting_usr_get_restaurant_promotions', kwargs={'restaurant': self.restaurant.pk, 'branch': self.pk, 'slug': self.restaurant.slug})
		}
		

class RestaurantImage(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	image = models.ImageField(upload_to=restaurant_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant.name

	def __unicode__(self):
		return self.restaurant.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class CategoryRestaurant(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	category = models.ForeignKey(RestaurantCategory, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant

	def __unicode__(self):
		return self.restaurant

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'category': self.category.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Administrator(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	token = models.TextField(null=False, blank=False)
	name = models.CharField(max_length=200, null=False, blank=False)
	username = models.CharField(max_length=100, null=False, blank=False, unique=True)
	email = models.EmailField(null=False, blank=False, unique=True)
	password = models.TextField(null=False, blank=False)
	phone = models.CharField(max_length=15, blank=False, null=False)
	image = models.ImageField(upload_to=administrator_image_path, null=False, blank=False)
	admin_type = models.CharField(max_length=100, null=False, blank=True)
	badge_number = models.CharField(max_length=200, null=True, blank=True)
	channel = models.CharField(max_length=255, null=True, blank=True)
	is_disabled = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def admin_type_str(self):
		return utils.get_from_tuple(utils.ADMIN_TYPE, self.admin_type)

	@property
	def bills(self):
		return Bill.objects.filter(admin=self.pk).order_by('-created_at')

	def bills_count(self):
		return self.bills.count()

	@property
	def placements(self):
		return Placement.objects.filter(waiter=self.pk).order_by('-created_at')

	def placements_count(self):
		return self.placements.count()

	@property
	def permissions(self):
		_permissions = AdminPermission.objects.get(admin=self.pk)
		return _permissions.permissions.split(',')

	def permissions_objs(self):
		return [Permission.objects.get(permission=perm) for perm in self.permissions]

	def has_permission(self, permission):
		return True if permission in self.permissions else False

	@property
	def messages(self):
		return PlacementMessage.objects.filter(placement__waiter__pk=self.pk, is_read=False).order_by('created_at')
	
	@property
	def messages_count(self):
		return self.messages.count()
	
	@property
	def socket_data(self):
		return {
			'id': self.pk,
			'type': 2,
			'name': self.name,
			'email': self.email,
			'image': self.image.url,
			'channel': self.channel
		}

	@property
	def to_data_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'email': self.email,
			'image': self.image.url
		}

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'branch': self.branch.to_json_s,
			'name': self.name,
			'username': self.username,
			'type': self.admin_type_str,
			'email': self.email,
			'phone': self.phone,
			'image': self.image.url,
			'badgeNumber': self.badge_number,
			'channel': self.channel,
			'permissions': self.permissions,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'username': self.username,
			'type': self.admin_type_str,
			'email': self.email,
			'phone': self.phone,
			'image': self.image.url,
			'badgeNumber': self.badge_number,
			'channel': self.channel,
			'permissions': self.permissions,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'branch': self.branch.to_json_admin,
			'token': self.token,
			'name': self.name,
			'username': self.username,
			'type': self.admin_type,
			'email': self.email,
			'phone': self.phone,
			'image': self.image.url,
			'badgeNumber': self.badge_number,
			'isDisabled': self.is_disabled,
			'channel': self.channel,
			'permissions': self.permissions,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class AdministratorResetPassword(models.Model):
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	email = models.EmailField(max_length=200, null=False, blank=False)
	token = models.TextField(null=False, blank=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expired_at = models.DateTimeField(null=False, blank=False)

	def __str__(self):
		return self.email

	def __unicode__(self):
		return self.email


class AdminPermission(models.Model):
	admin = models.OneToOneField(Administrator, on_delete=models.PROTECT)
	permissions = models.TextField(null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.admin

	def __unicode__(self):
		return self.admin


class RestaurantTable(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	waiter = models.ForeignKey(Administrator, null=True, blank=True, on_delete=models.PROTECT)
	uuid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	max_people = models.IntegerField(null=False, blank=False)
	number = models.CharField(max_length=20, null=False, blank=False)
	location = models.IntegerField(null=False, blank=False)
	chair_type = models.IntegerField(null=False, blank=False)
	description = models.TextField(null=False, blank=False)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.number

	def __unicode__(self):
		return self.number

	@property
	def location_str(self):
		return utils.get_from_tuple(utils.TABLE_LOCATION, self.location)
	
	@property
	def chair_type_str(self):
		return utils.get_from_tuple(utils.CHAIR_TYPE, self.chair_type)
	
	@property
	def placements(self):
		return Placement.objects.filter(table=self.pk).order_by('-created_at')

	def placements_count(self):
		return self.placements.count()

	@property
	def bookings(self):
		return Booking.objects.filter(table=self.pk).order_by('-created_at')

	def bookings_count(self):
		return self.bookings.count()

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'branch': self.branch.to_json_s,
			'uuid': self.uuid,
			'maxPeople': self.max_people,
			'number': self.number,
			'location': self.location_str,
			'chairType': self.chair_type_str,
			'description': self.description,
			'isAvailable': self.is_available,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'uuid': self.uuid,
			'maxPeople': self.max_people,
			'number': self.number,
			'location': self.location_str,
			'chairType': self.chair_type_str,
			'description': self.description,
			'isAvailable': self.is_available,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'waiter': self.waiter.to_json_s if self.waiter != None else None,
			'uuid': self.uuid,
			'maxPeople': self.max_people,
			'number': self.number,
			'location': self.location,
			'chairType': self.chair_type,
			'description': self.description,
			'isAvailable': self.is_available,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin_s(self):
		return {
			'id': self.pk,
			'uuid': self.uuid,
			'maxPeople': self.max_people,
			'number': self.number,
			'location': self.location,
			'chairType': self.chair_type,
			'description': self.description,
			'isAvailable': self.is_available,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class RestaurantConfig(models.Model):
	restaurant = models.OneToOneField(Restaurant, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, null=True, blank=True, on_delete=models.PROTECT)
	currency = models.CharField(max_length=100, null=True, blank=True)
	use_default_currency = models.BooleanField(default=False)
	languages = models.CharField(max_length=254, blank=True, null=True)
	tax = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	phone = models.CharField(max_length=255, null=True, blank=True)
	assign_table_to_waiter = models.BooleanField(default=True)
	cancel_late_booking = models.IntegerField(null=True, blank=True, default=30)
	waiter_see_all_orders = models.BooleanField(default=False)
	book_with_advance = models.BooleanField(default=False)
	booking_advance = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True)
	booking_cancelation_refund = models.BooleanField(default=False)
	booking_cancelation_refund_percent = models.DecimalField(max_digits=18, decimal_places=2, default=50.00)
	booking_payement_mode = models.IntegerField(default=3)
	days_before_reservation = models.IntegerField(default=3)
	can_take_away = models.BooleanField(default=True)
	user_should_pay_before = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant.name

	def __unicode__(self):
		return self.restaurant.name

	@property
	def payement_mode(self):
		return utils.get_from_tuple(utils.BOOKING_PAYEMENT_MODE, self.booking_payement_mode)

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'currency': self.currency,
			'tax': self.tax,
			'email': self.email,
			'phone': self.phone,
			'cancelLateBooking': self.cancel_late_booking,
			'bookWithAdvance': self.book_with_advance,
			'bookingAdvance': self.booking_advance,
			'bookingPaymentMode': self.payement_mode,
			'bookingCancelationRefund': self.booking_cancelation_refund,
			'bookingCancelationRefundPercent': self.booking_cancelation_refund_percent,
			'daysBeforeReservation': self.days_before_reservation,
			'canTakeAway': self.can_take_away,
			'userShouldPayBefore': self.user_should_pay_before
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'currency': self.currency,
			'tax': self.tax,
			'email': self.email,
			'phone': self.phone,
			'cancelLateBooking': self.cancel_late_booking,
			'bookWithAdvance': self.book_with_advance,
			'bookingAdvance': self.booking_advance,
			'bookingPaymentMode': self.booking_payement_mode,
			'bookingCancelationRefund': self.booking_cancelation_refund,
			'bookingCancelationRefundPercent': self.booking_cancelation_refund_percent,
			'daysBeforeReservation': self.days_before_reservation,
			'canTakeAway': self.can_take_away,
			'userShouldPayBefore': self.user_should_pay_before
		}


class RestaurantLicenceKey(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	key = models.ForeignKey(TingLicenceKey, on_delete=models.PROTECT)
	is_active = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.key

	def __unicode__(self):
		return self.key


class User(models.Model):
	token = models.TextField(null=False, blank=False)
	name = models.CharField(max_length=200, null=False, blank=False)
	username = models.CharField(max_length=100, null=False, blank=False, unique=True)
	email = models.EmailField(null=False, blank=False, unique=True)
	password = models.TextField(null=False, blank=False)
	image = models.ImageField(upload_to=user_image_path, null=False, blank=False)
	phone = models.CharField(max_length=15, blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=20, blank=False, null=False)
	country = models.CharField(max_length=200, null=False, blank=False)
	town = models.CharField(max_length=255, null=False, blank=False)
	channel = models.CharField(max_length=255, null=True, blank=True)
	is_authenticated = models.BooleanField(default=False)
	is_top = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def categories(self):
		return UserCategory.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def categories_count(self):
		return self.categories.count()

	@property
	def restaurants(self):
		return UserRestaurant.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def restaurants_count(self):
		return self.restaurants.count()

	@property
	def restaurant_reviews(self):
		return RestaurantReview.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def restaurant_reviews_count(self):
		return self.restaurant_reviews.count()

	@property
	def menu_reviews(self):
		return MenuReview.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def menu_reviews_count(self):
		return self.menu_reviews.count()

	@property
	def bookings(self):
		return Booking.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def bookings_count(self):
		return self.bookings.count()

	@property
	def placements(self):
		return Placement.objects.filter(user=self.pk).order_by('-created_at')

	@property
	def placements_count(self):
		return self.placements.count()

	@property
	def addresses(self):
		return UserAddress.objects.filter(user__pk=self.pk)

	@property
	def addresses_count(self):
		return self.addresses.count()

	@property
	def map_ping_svg_name(self):
		namedata = self.image.url.split('/')
		name = namedata[len(namedata) - 1]
		svgname = '%s.svg' % name.split('.')[0]
		return svgname
	
	@property
	def map_pin_svg(self):
		return '/tinguploads/users/pins/' + self.map_ping_svg_name
	
	def get_cover_base64(self):
		return utils.image_as_base64(self.image.path)

	@property
	def get_pin_base64(self):
		return utils.image_as_base64(self.map_pin_svg).replace('data:image/png;base64,', '')

	@property
	def get_pin_string(self):
		file = open('tinguploads/users/pins/' + self.map_ping_svg_name, 'r')
		return file.read()

	@property
	def socket_data(self):
		return {
			'id': self.pk,
			'type': 3,
			'name': self.name,
			'email': self.email,
			'image': self.image.url,
			'channel': self.channel
		}

	@property
	def to_data_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'email': self.email,
			'image': self.image.url
		}
	
	@property
	def to_json(self):
		return {
			'id': self.pk,
			'token': self.token,
			'name': self.name,
			'username': self.username,
			'email': self.email,
			'image': self.image,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'phone': self.phone,
			'dob': self.date_of_birth,
			'gender': self.gender,
			'country': self.country,
			'town': self.town,
			'channel': self.channel,
			'restaurants': {
				'count': self.restaurants_count,
				'restaurants': [restaurant.to_json_u for restaurant in self.restaurants]
			},
			'reviews': {
				'count': self.restaurant_reviews_count,
				'reviews': [review.to_json_u for review in self.restaurant_reviews]
			},
			'addresses': {
				'count': self.addresses_count,
				'addresses': [address.to_json for address in self.addresses]
			},
			'urls':{
				'loadRestaurants': reverse('ting_usr_load_restaurants', kwargs={'user': self.pk}),
				'loadReservations': reverse('ting_usr_load_reservations', kwargs={'user': self.pk}),
				'apiGet': reverse('api_user_get', kwargs={'user': self.pk}),
				'apiGetAuth': reverse('api_user_get_auth'),
				'apiRestaurants': '',
				'apiReservations': '',
				'apiMoments': '',
				'apiOrders': ''
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_u(self):

		return {
			'id': self.pk,
			'name': self.name,
			'username': self.username,
			'email': self.email,
			'image': self.image,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'phone': self.phone,
			'dob': self.date_of_birth,
			'gender': self.gender,
			'country': self.country,
			'town': self.town,
			'channel': self.channel,
			'restaurants': {
				'count': self.restaurants_count,
				'restaurants': [restaurant.to_json_u for restaurant in self.restaurants]
			},
			'reviews': {
				'count': self.restaurant_reviews_count,
				'reviews': [review.to_json_u for review in self.restaurant_reviews]
			},
			'addresses': {
				'count': self.addresses_count
			},
			'urls':{
				'loadRestaurants': reverse('ting_usr_load_restaurants', kwargs={'user': self.pk}),
				'loadReservations': reverse('ting_usr_load_reservations', kwargs={'user': self.pk}),
				'apiGet': reverse('api_user_get', kwargs={'user': self.pk}),
				'apiGetAuth': reverse('api_user_get_auth'),
				'apiRestaurants': '',
				'apiReservations': '',
				'apiMoments': '',
				'apiOrders': ''
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_b(self):
		return {
			'id': self.pk,
			'name': self.name,
			'username': self.username,
			'email': self.email,
			'image': self.image,
			'pin': self.map_pin_svg,
			'phone': self.phone,
			'dob': self.date_of_birth,
			'gender': self.gender,
			'country': self.country,
			'town': self.town,
			'channel': self.channel,
			'urls':{
				'loadRestaurants': reverse('ting_usr_load_restaurants', kwargs={'user': self.pk}),
				'loadReservations': reverse('ting_usr_load_reservations', kwargs={'user': self.pk}),
				'apiGet': reverse('api_user_get', kwargs={'user': self.pk}),
				'apiGetAuth': reverse('api_user_get_auth'),
				'apiRestaurants': '',
				'apiReservations': '',
				'apiMoments': '',
				'apiOrders': ''
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'username': self.username,
			'email': self.email,
			'image': self.image,
			'pin': self.map_pin_svg,
			'pinImg': self.map_pin_svg,
			'phone': self.phone,
			'dob': self.date_of_birth,
			'gender': self.gender,
			'country': self.country,
			'town': self.town,
			'channel': self.channel,
			'urls':{
				'loadRestaurants': reverse('ting_usr_load_restaurants', kwargs={'user': self.pk}),
				'loadReservations': reverse('ting_usr_load_reservations', kwargs={'user': self.pk}),
				'apiGet': reverse('api_user_get', kwargs={'user': self.pk}),
				'apiGetAuth': reverse('api_user_get_auth'),
				'apiRestaurants': '',
				'apiReservations': '',
				'apiMoments': '',
				'apiOrders': ''
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_admin_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'username': self.username,
			'email': self.email,
			'image': self.image,
			'phone': self.phone,
			'dob': self.date_of_birth,
			'gender': self.gender,
			'country': self.country,
			'town': self.town,
			'channel': self.channel,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class UserAddress(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	type = models.CharField(null=False, blank=False, max_length=200)
	address = models.TextField(null=False, blank=False)
	latitude = models.CharField(max_length=200, null=False, blank=False)
	longitude = models.CharField(max_length=200, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address

	def __unicode__(self):
		return self.address

	@property
	def type_icon(self):
		if self.type.lower() == 'home':
			return 'lnr-home'
		elif self.type.lower() == 'work':
			return 'lnr-briefcase'
		elif self.type.lower() == 'school':
			return 'lnr-graduation-hat'
		else:
			return 'lnr-map-marker'

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'type': self.type,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class UserCategory(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	category = models.ForeignKey(RestaurantCategory, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_b,
			'category': self.category.to_json,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class UserResetPassword(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	email = models.EmailField(max_length=200, null=False, blank=False)
	token = models.TextField(null=False, blank=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expired_at = models.DateTimeField(null=False, blank=False)

	def __str__(self):
		return self.email

	def __unicode__(self):
		return self.email


class UserRestaurant(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'branch': self.branch.to_json_s,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_u(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'branch': self.branch.to_json_u,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class RestaurantReview(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	review = models.IntegerField(null=False, blank=False)
	comment = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_u(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_b(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class UserNotification(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	from_type = models.IntegerField(null=False, blank=False) # user, restaurant
	from_id = models.IntegerField(null=False, blank=False)
	message = models.CharField(max_length=255, null=False, blank=False)
	notif_type = models.CharField(max_length=100, null=False, blank=False)
	url = models.CharField(max_length=255, null=False, blank=False)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message

	def __unicode__(self):
		return self.message


### MENU AND FOOD


class FoodCategory(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	description = models.TextField(blank=True, null=True)
	image = models.ImageField(upload_to=category_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	def foods_count(self):
		return self.foods.count()

	@property
	def appetizers(self):
		return Food.objects.filter(category=self.pk, food_type=1).order_by('-created_at')

	def appetizers_count(self):
		return self.appetizers.count()

	@property
	def meals(self):
		return Food.objects.filter(category=self.pk, food_type=2).order_by('-created_at')

	def meals_count(self):
		return self.meals.count()

	@property
	def desserts(self):
		return Food.objects.filter(category=self.pk, food_type=3).order_by('-created_at')

	def desserts_count(self):
		return self.desserts.count()

	@property
	def sauces(self):
		return Food.objects.filter(category=self.pk, food_type=4).order_by('-created_at')

	def sauces_count(self):
		return self.sauces.count()

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'description': self.description,
			'image': self.image.url,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Food(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT)
	cuisine = models.ForeignKey(RestaurantCategory, null=True, blank=True, on_delete=models.PROTECT)
	food_type = models.IntegerField(null=False, blank=False)
	description = models.TextField(blank=True, null=True)
	ingredients = models.TextField(blank=True, null=True)
	show_ingredients = models.BooleanField(default=True)
	price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	last_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
	currency = models.CharField(max_length=50, null=False, blank=False)
	is_countable = models.BooleanField(default=False)
	quantity = models.IntegerField(default=1)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def type_str(self):
		return utils.get_from_tuple(utils.FOOD_TYPE, self.food_type)

	@property
	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=1, menu_id=self.pk)

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def likes(self):
		return MenuLike.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def likes_count(self):
		return self.likes.count()

	@property
	def images(self):
		return FoodImage.objects.filter(food=self.pk).order_by('created_at')

	@property
	def image(self):
		return self.images[0].image.url
	
	@property
	def promotions(self):
		return Promotion.objects.filter(Q(promotion_menu_type='00') | 
				Q(promotion_menu_type='01') | Q(menu__pk=self.menu.pk) |
				Q(category__pk=self.category.pk)).filter(branch__pk=self.branch.pk, is_on=True).order_by('-created_at')

	@property
	def promotions_count(self):
		return self.promotions.count()

	@property
	def today_promotion_object(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0] if len(promos) > 0 else None

	@property
	def today_promotion(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0].string_data_json if len(promos) > 0 else None

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_u,
			'branch': self.branch.to_json_u,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_f(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json,
			'branch': self.branch.to_json,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_r(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_p(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_f_s(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'foodTypeId' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'foodType' : self.food_type,
			'price': self.price,
			'currency': self.currency,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'menu': self.menu.pk,
			'type': 1,
			'foodType' : self.food_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	def json_search(self, queries):
		return  {
			'id': self.menu.pk,
			'type': 2,
			'image': self.image,
			'name': self.name,
			'description': '%s, %s' % (self.branch.name, self.restaurant.name),
			'text': '%s %s' % (self.currency, intcomma(self.price)),
			'reviews': self.reviews_count,
			'reviewAverage': self.review_average,
			'qp': utils.query_priority(self.name, queries),
			'coords': {'lat': self.branch.latitude, 'lng': self.branch.longitude},
			'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.menu.pk}),
			'relative': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug})
		}


class FoodImage(models.Model):
	food = models.ForeignKey(Food, on_delete=models.PROTECT)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.food

	def __unicode__(self):
		return self.food

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image.url,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Drink(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	drink_type = models.IntegerField(null=False, blank=False)
	description = models.TextField(blank=True, null=True)
	ingredients = models.TextField(blank=True, null=True)
	show_ingredients = models.BooleanField(default=True)
	price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	last_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
	currency = models.CharField(max_length=50, null=False, blank=False)
	is_countable = models.BooleanField(default=False)
	quantity = models.IntegerField(default=1)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def type_str(self):
		return utils.get_from_tuple(utils.DRINK_TYPE, self.drink_type)

	@property
	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=2, menu_id=self.pk)

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def likes(self):
		return MenuLike.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def likes_count(self):
		return self.likes.count()

	@property
	def images(self):
		return DrinkImage.objects.filter(drink=self.pk).order_by('-created_at')

	@property
	def image(self):
		return self.images[0].image.url

	@property
	def promotions(self):
		return Promotion.objects.filter(Q(promotion_menu_type='00') | 
				Q(promotion_menu_type='02') | Q(menu__pk=self.menu.pk) ).filter(branch__pk=self.branch.pk, is_on=True).order_by('-created_at')

	@property
	def promotions_count(self):
		return self.promotions.count()

	@property
	def today_promotion_object(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0] if len(promos) > 0 else None

	@property
	def today_promotion(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0].string_data_json if len(promos) > 0 else None

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_u,
			'branch': self.branch.to_json_u,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_f(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json,
			'branch': self.branch.to_json,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_r(self):
		return {
			'id': self.pk,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_p(self):
		return {
			'id': self.pk,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_f_s(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'name': self.name,
			'drinkTypeId': self.drink_type,
			'drinkType': self.type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'name': self.name,
			'menu': self.menu.pk,
			'type': 2,
			'drinkType' : self.drink_type,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'drinkType' : self.drink_type,
			'price': self.price,
			'currency': self.currency,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	def json_search(self, queries):
		return  {
			'id': self.menu.pk,
			'type': 2,
			'image': self.image,
			'name': self.name,
			'description': '%s, %s' % (self.branch.name, self.restaurant.name),
			'text': '%s %s' % (self.currency, intcomma(self.price)),
			'reviews': self.reviews_count,
			'reviewAverage': self.review_average,
			'qp': utils.query_priority(self.name, queries),
			'coords': {'lat': self.branch.latitude, 'lng': self.branch.longitude},
			'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.menu.pk}),
			'relative': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug})
		}


class DrinkImage(models.Model):
	drink = models.ForeignKey(Drink, on_delete=models.PROTECT)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.drink

	def __unicode__(self):
		return self.drink

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image.url,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Dish(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT)
	cuisine = models.ForeignKey(RestaurantCategory, null=True, blank=True, on_delete=models.PROTECT)
	dish_time = models.IntegerField(null=False, blank=False)
	description = models.TextField(blank=True, null=True)
	ingredients = models.TextField(blank=True, null=True)
	show_ingredients = models.BooleanField(default=True)
	price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	last_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
	currency = models.CharField(max_length=50, null=False, blank=False)
	is_countable = models.BooleanField(default=False)
	quantity = models.IntegerField(default=1)
	is_available = models.BooleanField(default=True)
	has_drink = models.BooleanField(default=False)
	drink = models.ForeignKey(Drink, null=True, blank=True, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def dish_time_str(self):
		return utils.get_from_tuple(utils.DISH_TIME, self.dish_time)

	@property
	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=3, menu_id=self.pk)

	@property
	def foods(self):
		return DishFood.objects.filter(dish=self.pk).order_by('-created_at')

	@property
	def foods_ids(self):
		return [food.food.id for food in self.foods]

	@property
	def foods_count(self):
		return self.foods.count()

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def likes(self):
		return MenuLike.objects.filter(menu=self.menu.pk).order_by('-created_at')

	@property
	def likes_count(self):
		return self.likes.count()

	@property
	def images(self):
		return DishImage.objects.filter(dish=self.pk).order_by('-created_at')

	@property
	def image(self):
		return self.images[0].image.url

	@property
	def promotions(self):
		return Promotion.objects.filter(Q(promotion_menu_type='00') | 
				Q(promotion_menu_type='03') | Q(menu__pk=self.menu.pk) |
				Q(category__pk=self.category.pk)).filter(branch__pk=self.branch.pk, is_on=True).order_by('-created_at')

	@property
	def promotions_count(self):
		return self.promotions.count()

	@property
	def today_promotion_object(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0] if len(promos) > 0 else None

	@property
	def today_promotion(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0].string_data_json if len(promos) > 0 else None

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_u,
			'branch': self.branch.to_json_u,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_r if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_f(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json,
			'branch': self.branch.to_json,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_r if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_r(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_r if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_p(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_r if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_s if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_f_s(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'dishTimeId': self.dish_time,
			'dishTime': self.dish_time_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_r if self.has_drink == True else {},
			'url': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug}),
			'promotions':{
				'count': self.promotions_count,
				'todayPromotion': self.today_promotion,
				'promotions': [promo.to_json for promo in self.promotions]
			},
			'reviews': {
				'count': self.reviews_count,
				'average': self.review_average,
				'percents': self.review_percent,
				'reviews': [review.to_json for review in self.reviews[:5]]
			},
			'likes': {
				'count': self.likes_count,
				'likes': self.menu.like_ids
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_s for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'name': self.name,
			'category': self.category.to_json,
			'cuisine': self.cuisine.to_json,
			'menu': self.menu.pk,
			'type': 3,
			'dishTime' : self.dish_time,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json_admin if self.has_drink == True else None,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'foods': {
				'count': self.foods_count,
				'foods': [food.to_json_admin for food in self.foods]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin_s(self):
		return {
			'id': self.pk,
			'name': self.name,
			'dishTime' : self.dish_time,
			'price': self.price,
			'currency': self.currency,
			'isAvailable': self.is_available,
			'quantity': self.quantity,
			'images':{
				'count': self.images.count(),
				'images': [image.to_json for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	def json_search(self, queries):
		return  {
			'id': self.menu.pk,
			'type': 2,
			'image': self.image,
			'name': self.name,
			'description': '%s, %s' % (self.branch.name, self.restaurant.name),
			'text': '%s %s' % (self.currency, intcomma(self.price)),
			'reviews': self.reviews_count,
			'reviewAverage': self.review_average,
			'qp': utils.query_priority(self.name, queries),
			'coords': {'lat': self.branch.latitude, 'lng': self.branch.longitude},
			'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.menu.pk}),
			'relative': reverse('ting_usr_menu_get', kwargs={'menu': self.menu.pk, 'slug': self.slug})
		}


class DishImage(models.Model):
	dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.dish

	def __unicode__(self):
		return self.dish

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image.url,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class DishFood(models.Model):
	dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
	food = models.ForeignKey(Food, on_delete=models.PROTECT)
	is_countable = models.BooleanField(default=False)
	quantity = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.food.name

	def __unicode__(self):
		return self.food.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'food': self.food.to_json_r,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'food': self.food.to_json_s,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'food': self.food.pk,
			'menu': self.food.menu.pk,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Menu(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	name = models.CharField(max_length=200, null=True, blank=True)
	menu_type = models.IntegerField(null=False, blank=False)
	menu_id = models.IntegerField(null=False, blank=False)
	for_all_branches = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.menu_type

	def __unicode__(self):
		return self.menu_type

	@property
	def menu_type_str(self):
		return utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)

	@property
	def menu_type_icon(self):
		if self.menu_type == 1:
			return 'utensil spoon'
		elif self.menu_type == 2:
			return 'glass martini'
		elif self.menu_type == 3:
			return 'utensils'
		else:
			return ''

	@property
	def menu_type_quantifier(self):
		if self.menu_type == 1:
			return 'Packs / Pieces'
		elif self.menu_type == 2:
			return 'Bottles / Cups'
		elif self.menu_type == 3:
			return 'Plates / Packs'
		else:
			return ''

	@property
	def food(self):
		return Food.objects.get(pk=self.menu_id)

	@property
	def drink(self):
		return Drink.objects.get(pk=self.menu_id)
	
	@property
	def dish(self):
		return Dish.objects.get(pk=self.menu_id)

	@property
	def menu(self):
		if self.menu_type == 1:
			return self.food
		elif self.menu_type == 2:
			return self.drink
		elif self.menu_type == 3:
			return self.dish
		else:
			return None

	@property
	def slug(self):
		if self.menu_type == 1:
			return self.food.slug
		elif self.menu_type == 2:
			return self.drink.slug
		elif self.menu_type == 3:
			return self.dish.slug
		else:
			return ''

	@property
	def category(self):
		if self.menu_type == 1:
			return self.food.category
		elif self.menu_type == 2:
			return None
		elif self.menu_type == 3:
			return self.dish.category
		else:
			return None

	@property
	def cuisine(self):
		if self.menu_type == 1:
			return self.food.cuisine
		elif self.menu_type == 2:
			return None
		elif self.menu_type == 3:
			return self.dish.cuisine
		else:
			return None

	@property
	def type_str(self):
		if self.menu_type == 1:
			return self.food.type_str
		elif self.menu_type == 2:
			return drink.type_str
		elif self.menu_type == 3:
			return self.dish.dish_time_str
		else:
			return ''

	@property
	def description(self):
		if self.menu_type == 1:
			return self.food.description
		elif self.menu_type == 2:
			return self.drink.description
		elif self.menu_type == 3:
			return self.dish.description
		else:
			return ''

	@property
	def ingredients(self):
		if self.menu_type == 1:
			return self.food.ingredients
		elif self.menu_type == 2:
			return self.drink.ingredients
		elif self.menu_type == 3:
			return self.dish.ingredients
		else:
			return ''

	@property
	def show_ingredients(self):
		if self.menu_type == 1:
			return self.food.show_ingredients
		elif self.menu_type == 2:
			return self.drink.show_ingredients
		elif self.menu_type == 3:
			return self.dish.show_ingredients
		else:
			return False

	@property
	def price(self):
		if self.menu_type == 1:
			return self.food.price
		elif self.menu_type == 2:
			return self.drink.price
		elif self.menu_type == 3:
			return self.dish.price
		else:
			return 0

	@property
	def last_price(self):
		if self.menu_type == 1:
			return self.food.last_price
		elif self.menu_type == 2:
			return self.drink.last_price
		elif self.menu_type == 3:
			return self.dish.last_price
		else:
			return 0

	@property
	def currency(self):
		if self.menu_type == 1:
			return self.food.currency
		elif self.menu_type == 2:
			return self.drink.currency
		elif self.menu_type == 3:
			return self.dish.currency
		else:
			return ''

	@property
	def is_countable(self):
		if self.menu_type == 1:
			return self.food.is_countable
		elif self.menu_type == 2:
			return self.drink.is_countable
		elif self.menu_type == 3:
			return self.dish.is_countable
		else:
			return False

	@property
	def quantity(self):
		if self.menu_type == 1:
			return self.food.quantity
		elif self.menu_type == 2:
			return self.drink.quantity
		elif self.menu_type == 3:
			return self.dish.quantity
		else:
			return 0

	@property
	def is_available(self):
		if self.menu_type == 1:
			return self.food.is_available
		elif self.menu_type == 2:
			return self.drink.is_available
		elif self.menu_type == 3:
			return self.dish.is_available
		else:
			return False

	@property
	def images(self):
		if self.menu_type == 1:
			return self.food.images
		elif self.menu_type == 2:
			return self.drink.images
		elif self.menu_type == 3:
			return self.dish.images
		else:
			return []

	@property
	def likes(self):
		return MenuLike.objects.filter(menu=self.pk).order_by('-created_at')

	@property
	def likes_count(self):
		return self.likes.count()
	
	@property
	def like_ids(self):
		return [like.user.pk for like in self.likes]
	
	def has_liked(self, u):
		return True if u in self.like_ids else False

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.pk).order_by('-created_at')

	@property
	def reviews_count(self):
		return self.reviews.count()

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	@property
	def review_average(self):
		return round(sum([review.review for review in self.reviews]) / self.reviews_count, 1) if self.reviews_count > 0 else 0

	def review_percent_calculation(self, stars):
		reviews = self.reviews.filter(review=stars).count()
		return (reviews * 100) / self.reviews_count if reviews != 0 else 0

	@property
	def review_percent(self):
		return [self.review_percent_calculation(n) for n in range(1, 6)]

	@property
	def image(self):
		return self.images[0].image.url

	@property
	def promotions(self):
		return Promotion.objects.filter(Q(promotion_menu_type='00') | 
				Q(promotion_menu_type='0%s' % menu.menu_type) | Q(menu__pk=self.menu.pk) ).filter(branch__pk=self.branch.pk, is_on=True).order_by('-created_at')

	@property
	def promotions_count(self):
		return self.promotions.count()

	@property
	def today_promotion_object(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0] if len(promos) > 0 else None

	@property
	def today_promotion(self):
		promos = list(filter(lambda p: p.is_on_today == True, self.promotions))
		return promos[0].string_data_json if len(promos) > 0 else None

	@property
	def to_json(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
				'menu': food.to_json_r
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
				'menu': drink.to_json_r
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
				'menu': dish.to_json_r
			}

	@property
	def to_json_p(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
				'menu': food.to_json_p
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
				'menu': drink.to_json_p
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
				'menu': dish.to_json_p
			}
	
	@property
	def to_json_f(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
				'menu': food.to_json_f
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
				'menu': drink.to_json_f
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
				'menu': dish.to_json_f
			}

	@property
	def to_json_s(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
				'menu': food.to_json_s
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
				'menu': drink.to_json_s
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
				'menu': dish.to_json_s
			}

	@property
	def to_json_f_s(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': food.slug}),
				'menu': food.to_json_f_s
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': drink.slug}),
				'menu': drink.to_json_f_s
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'restaurant': {
					'name': '%s, %s' % (self.restaurant.name, self.branch.name),
					'logo': self.restaurant.logo.url
				},
				'forAllBranches': self.for_all_branches,
				'urls':{
					'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
					'like': reverse('ting_usr_menu_like', kwargs={'menu': self.pk}),
					'loadReviews': reverse('ting_usr_menu_load_reviews', kwargs={'menu': self.pk}),
					'addReview': reverse('ting_usr_menu_add_review', kwargs={'menu': self.pk}),
					'apiGet': reverse('api_restaurant_menu_get', kwargs={'menu': self.pk}),
					'apiLike': reverse('api_restaurant_menu_like', kwargs={'menu': self.pk}),
					'apiReviews': reverse('api_restaurant_menu_reviews', kwargs={'menu': self.pk}),
					'apiAddReview': reverse('api_restaurant_menu_add_review', kwargs={'menu': self.pk}),
				},
				'url': reverse('ting_usr_menu_get', kwargs={'menu': self.pk, 'slug': dish.slug}),
				'menu': dish.to_json_f_s
			}

	@property
	def to_json_admin(self):
		if self.menu_type == 1:
			food = Food.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'forAllBranches': self.for_all_branches,
				'menu': food.to_json_admin_s
			}
		elif self.menu_type == 2:
			drink = Drink.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'forAllBranches': self.for_all_branches,
				'menu': drink.to_json_admin_s
			}
		elif self.menu_type == 3:
			dish = Dish.objects.get(pk=self.menu_id)
			return {
				'id': self.pk,
				'type':{
					'id': self.menu_type,
					'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
				},
				'forAllBranches': self.for_all_branches,
				'menu': dish.to_json_admin_s
			}


class MenuReview(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
	review = models.IntegerField(null=False, blank=False)
	comment = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_b,
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class MenuLike(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_b,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Promotion(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	admin = models.ForeignKey(Administrator, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	uuid = models.CharField(max_length=100, null=False, blank=False)
	occasion_event = models.CharField(max_length=200, null=False, blank=False)
	promotion_menu_type = models.CharField(max_length=100, null=False, blank=False)
	menu = models.ForeignKey(Menu, null=True, blank=True, related_name='menu', on_delete=models.PROTECT)
	category = models.ForeignKey(FoodCategory, null=True, blank=True, on_delete=models.PROTECT)
	has_reduction = models.BooleanField(default=True)
	amount = models.IntegerField(null=True, blank=True, default=0)
	reduction_type = models.CharField(max_length=100, null=True, blank=True) # Currency Or %
	has_supplement = models.BooleanField(default=False)
	supplement_min_quantity = models.IntegerField(default=1, null=False, blank=False)
	is_supplement_same = models.BooleanField(default=False)
	supplement = models.ForeignKey(Menu, null=True, blank=True, related_name='supplement', on_delete=models.PROTECT)
	supplement_quantity = models.IntegerField(default=1, null=False, blank=False)
	is_on = models.BooleanField(default=True)
	promotion_period = models.CharField(max_length=100, null=True, blank=True)
	is_special = models.BooleanField(default=False)
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)
	poster_image = models.ImageField(upload_to=promotion_image_path, null=False, blank=False)
	description = models.TextField(null=False, blank=False)
	for_all_branches = models.BooleanField(default=False)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now_add=True)

	objects = RandomManager()

	def __str__(self):
		return self.occasion_event

	def __unicode__(self):
		return self.occasion_event

	@property
	def uuid_url(self):
		return '%s-%s' % (self.occasion_event.replace(' ', '-').lower(), self.uuid)

	@property
	def interess_url(self):
		return reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk})

	@property
	def promo_type(self):
		return utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)

	@property
	def promo_type_html(self):
		if self.promotion_menu_type == '05':
			return """<div class="ui relaxed horizontal list">
						<div class="item">
                            <img class="ui avatar image" src="%s">
                            <div class="content">
                               	<a class="header" style="font-weight: normal;">%s</a>
                            </div>
                        </div>
                    </div>""" % (self.category.image.url, self.category.name)
		elif self.promotion_menu_type == '04':
			return """<div class="ui relaxed horizontal list">
						<div class="item">
                            <img class="ui avatar image" src="%s">
                            <div class="content">
                               	<a class="header" style="font-weight: normal;">%s</a>
                            </div>
                        </div>
                    </div>""" % (get_menu_image(self.menu.pk), get_menu_name(self.menu.pk))
		else:
			return self.promo_type

	@property
	def interests(self):
		return PromotionInterest.objects.filter(promotion=self.pk)

	@property
	def interests_count(self):
		return self.interests.count()

	@property
	def interests_ids(self):
		return [interest.user.pk for interest in self.interests]

	def has_user_interest(self, u):
		return True if u in self.interests_ids else False

	@property
	def promo_period(self):
		if self.is_special == True:
			return '%s - %s' % (self.start_date.strftime('%a, %d %B %Y'), self.end_date.strftime('%a, %d %B %Y'))
		else:
			return ', '.join([utils.get_from_tuple(utils.PROMOTION_PERIOD, period) for period in self.promotion_period.split(',')])

	@property
	def reduction(self):
		return '%s %s' % (self.amount, self.reduction_type) if self.has_reduction else 'None'

	@property
	def reduction_string(self):
		return 'Order this menu and get %s' % self.reduction if self.has_reduction else None
	
	@property
	def supplement_string(self):
		if self.has_supplement:
			if self.is_supplement_same == False:
				if self.supplement.menu_type == 1:
					menu = Food.objects.get(pk=self.supplement.menu_id)
					return 'Order %s of this menu and get %s free %s' % (self.supplement_min_quantity, self.supplement_quantity, menu.name)
				elif self.supplement.menu_type == 2:
					menu = Drink.objects.get(pk=self.supplement.menu_id)
					return 'Order %s of this menu and get %s free %s' % (self.supplement_min_quantity, self.supplement_quantity, menu.name)
				elif self.supplement.menu_type == 3:
					menu = Food.objects.get(pk=self.supplement.menu_id)
					return 'Order %s of this menu and get %s free %s' % (self.supplement_min_quantity, self.supplement_quantity, menu.name)
			else:
				return 'Order %s of this menu and get %s more for free' % (self.supplement_min_quantity, self.supplement_quantity)
		else:
			return None
	
	@property
	def is_on_today(self):
		today = date.today()
		if self.is_special == True:
			return True if today >= self.start_date and today < self.end_date else False
		else:
			periods = self.promotion_period.split(',')
			if str(1) in periods:
				return True
			else:
				dayofw = today.strftime('%w')
				if str(int(dayofw) + 1) in periods:
					return True
				elif str(8) in periods and (int(dayofw) == 6 or int(dayofw) == 0):
					return True
		return False

	@property
	def supplement_html(self):
		if self.has_supplement == True:
			if self.is_supplement_same == True:
				return '%s, Same Menu' % (self.supplement_quantity)
			else:
				return """<div class="ui relaxed horizontal list">
						<div class="item">
                            <img class="ui avatar image" src="%s">
                            <div class="content">
                               	<a class="header" style="font-weight: normal;">%s, %s</a>
                            </div>
                        </div>
                    </div>""" % (get_menu_image(self.supplement.pk), self.supplement_quantity, get_menu_name(self.supplement.pk))
		else:
			return 'None'

	@property
	def promoted_menus(self):
		if self.promotion_menu_type == '00':
			return [menu for menu in Menu.objects.filter(branch__pk=self.branch.pk)]
		elif self.promotion_menu_type == '01':
			return [menu for menu in Menu.objects.filter(branch__pk=self.branch.pk, menu_type=1)]
		elif self.promotion_menu_type == '02':
			return [menu for menu in Menu.objects.filter(branch__pk=self.branch.pk, menu_type=2)]
		elif self.promotion_menu_type == '03':
			return [menu for menu in Menu.objects.filter(branch__pk=self.branch.pk, menu_type=3)]
		elif self.promotion_menu_type == '04':
			return [self.menu]
		elif self.promotion_menu_type == '05':
			foods = [food.menu for food in Food.objects.filter(branch__pk=self.branch.pk, category__pk=self.category.pk)]
			dishes = [dish.menu for dish in Dish.objects.filter(branch__pk=self.branch.pk, category__pk=self.category.pk)]
			return foods + dishes
		else:
			return []

	@property
	def string_data_json(self):
		return {'id': self.pk, 'occasionEvent': self.occasion_event, 'posterImage': self.poster_image.url, 'supplement': self.supplement_string, 'reduction': self.reduction_string}

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'occasionEvent': self.occasion_event,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_p if self.promotion_menu_type == '04' else {}
			},
			'menus': {
				'count': len(self.promoted_menus)
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_p if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': self.promo_period,
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'interests':{
				'count': self.interests_count,
				'interests': self.interests_ids
			},
			'urls':{
				'relative': reverse('ting_usr_promotion_get', kwargs={'promotion': self.pk, 'slug': self.uuid_url}),
				'interest': reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk}),
				'apiGet': reverse('api_promotion_get', kwargs={'promo': self.pk}),
				'apiInterest': reverse('api_promotion_interest', kwargs={'promo': self.pk})
			},
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_f(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'occasionEvent': self.occasion_event,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_p if self.promotion_menu_type == '04' else {}
			},
			'menus': {
				'count': len(self.promoted_menus),
				'menus': [menu.to_json_s for menu in self.promoted_menus]
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_p if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': self.promo_period,
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'interests':{
				'count': self.interests_count,
				'interests': self.interests_ids
			},
			'urls':{
				'relative': reverse('ting_usr_promotion_get', kwargs={'promotion': self.pk, 'slug': self.uuid_url}),
				'interest': reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk}),
				'apiGet': reverse('api_promotion_get', kwargs={'promo': self.pk}),
				'apiInterest': reverse('api_promotion_interest', kwargs={'promo': self.pk})
			},
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_f_a(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'occasionEvent': self.occasion_event,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_p if self.promotion_menu_type == '04' else {}
			},
			'menus': {
				'count': len(self.promoted_menus),
				'menus': [menu.to_json_s for menu in random.sample(self.promoted_menus, k=4)] if len(self.promoted_menus) > 4 else [menu.to_json_s for menu in self.promoted_menus]
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_p if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': self.promo_period,
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'interests':{
				'count': self.interests_count,
				'interests': self.interests_ids
			},
			'urls':{
				'relative': reverse('ting_usr_promotion_get', kwargs={'promotion': self.pk, 'slug': self.uuid_url}),
				'interest': reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk}),
				'apiGet': reverse('api_promotion_get', kwargs={'promo': self.pk}),
				'apiInterest': reverse('api_promotion_interest', kwargs={'promo': self.pk})
			},
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_b(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json,
			'occasionEvent': self.occasion_event,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_p if self.promotion_menu_type == '04' else {}
			},
			'menus': {
				'count': len(self.promoted_menus)
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_p if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': self.promo_period,
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'interests':{
				'count': self.interests_count,
				'interests': self.interests_ids
			},
			'urls':{
				'relative': reverse('ting_usr_promotion_get', kwargs={'promotion': self.pk, 'slug': self.uuid_url}),
				'interest': reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk}),
				'apiGet': reverse('api_promotion_get', kwargs={'promo': self.pk}),
				'apiInterest': reverse('api_promotion_interest', kwargs={'promo': self.pk})
			},
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'occasionEvent': self.occasion_event,
			'restaurant': self.restaurant.to_json_s,
			'branch': self.branch.to_json_s,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_p if self.promotion_menu_type == '04' else {}
			},
			'menus': {
				'count': len(self.promoted_menus)
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_p if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': self.promo_period,
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'interests':{
				'count': self.interests_count,
				'interests': self.interests_ids
			},
			'urls':{
				'relative': reverse('ting_usr_promotion_get', kwargs={'promotion': self.pk, 'slug': self.uuid_url}),
				'interest': reverse('ting_usr_promotion_interest', kwargs={'promo': self.pk}),
				'apiGet': reverse('api_promotion_get', kwargs={'promo': self.pk}),
				'apiInterest': reverse('api_promotion_interest', kwargs={'promo': self.pk})
			},
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'occasionEvent': self.occasion_event,
			'uuid': self.uuid,
			'uuidUrl': self.uuid_url,
			'promotionItem': {
				'type':{'id': self.promotion_menu_type, 'name': utils.get_from_tuple(utils.PROMOTION_MENU, self.promotion_menu_type)},
				'category': self.category.to_json if self.promotion_menu_type == '05' else {},
				'menu': self.menu.to_json_admin if self.promotion_menu_type == '04' else {}
			},
			'reduction':{
				'hasReduction': self.has_reduction,
				'amount': self.amount,
				'reductionType': self.reduction_type
			},
			'supplement':{
				'hasSupplement': self.has_supplement,
				'minQuantity': self.supplement_min_quantity,
				'isSame': self.is_supplement_same,
				'supplement': self.supplement.to_json_admin if self.is_supplement_same == False else {},
				'quantity': self.supplement_quantity
			},
			'period': {
				'isSpecial': self.is_special,
				'startDate': self.start_date.strftime('%Y-%m-%d %H:%M:%S') if self.start_date != None else None,
				'endDate': self.end_date.strftime('%Y-%m-%d %H:%M:%S') if self.end_date != None else None,
				'periods': self.promotion_period.split(',') if self.promotion_period != None else []
			},
			'description': self.description,
			'posterImage': self.poster_image.url,
			'isOn': self.is_on,
			'isOnToday': self.is_on_today,
			'forAllBranches': self.for_all_branches,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class PromotionInterest(models.Model):
	promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	is_interested = models.BooleanField(default=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.promotion.occasion_event

	def __unicode__(self):
		return self.promotion.occasion_event

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'isInterested': self.is_interested,
			'createdAt': self.created_at
		}


### BOOK, ORDERS, BILLS


class Booking(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	table = models.ForeignKey(RestaurantTable, null=True, blank=True, on_delete=models.PROTECT)
	token = models.CharField(max_length=100, null=False, blank=False, unique=True)
	people = models.IntegerField(null=False, blank=False)
	location = models.IntegerField(null=False, blank=False)
	amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
	date = models.DateField(null=False, blank=False)
	time = models.TimeField(null=False, blank=False)
	status = models.IntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def status_str(self):
		return utils.get_from_tuple(utils.BOOKING_STATUSES, self.status)

	@property
	def location_str(self):
		return utils.get_from_tuple(utils.TABLE_LOCATION, self.location)

	@property
	def date_time(self):
		return datetime.combine(self.date, self.time)

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'branch': self.branch.to_json_s,
			'table': self.table.to_json_s if self.table != None else None,
			'token': self.token,
			'people': self.people,
			'date': self.date,
			'time': self.time,
			'status': self.status_str,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'token': self.token,
			'people': self.people,
			'date': self.date,
			'time': self.time,
			'status': self.status_str,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'table': self.table.to_json_admin_s if self.table != None else None,
			'token': self.token,
			'people': self.people,
			'date': self.date,
			'time': self.time,
			'location': self.location,
			'status': self.status,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}
	

class Bill(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	number = models.CharField(max_length=20, null=False, blank=False)
	token = models.CharField(max_length=200, null=False, blank=False, unique=True)
	placement_id = models.IntegerField(null=True, blank=True)
	amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	discount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	tips = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	extras_total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	currency = models.CharField(max_length=100, null=True, blank=True)
	is_requested = models.BooleanField(default=False)
	is_paid = models.BooleanField(default=False)
	is_complete = models.BooleanField(default=False)
	paid_by = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.number

	def __unicode__(self):
		return self.number

	@property	
	def orders(self):
		return Order.objects.filter(bill=self.pk, is_delivered=True).order_by('-created_at')

	@property
	def orders_count(self):
		return self.orders.count()

	@property
	def placement(self):
		return Placement.objects.get(pk=self.placement_id)

	@property
	def extras(self):
		return BillExtra.objects.filter(bill__pk=self.pk)

	@property
	def discount_value(self):
		return float('%.2f' % ((self.amount * self.discount) / 100))

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'number': self.number,
			'token': self.token,
			'amount': float(self.amount),
			'discount': float(self.discount),
			'tips': float( self.tips),
			'extrasTotal': float(self.extras_total),
			'total': float(self.total),
			'currency': self.currency,
			'isRequested': self.is_requested,
			'isPaid': self.is_paid,
			'isComplete': self.is_complete,
			'paidBy': self.paid_by,
			'orders': {
				'count': self.orders_count,
				'orders': [order.to_json_s for order in self.orders]
			},
			'extras': [extra.to_json for extra in self.extras],
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'number': self.number,
			'token': self.token,
			'amount': float(self.amount),
			'discount': float(self.discount),
			'tips': float( self.tips),
			'extrasTotal': float(self.extras_total),
			'total': float(self.total),
			'currency': self.currency,
			'isRequested': self.is_requested,
			'isPaid': self.is_paid,
			'isComplete': self.is_complete,
			'paidBy': self.paid_by,
			'orders': {
				'count': self.orders_count
			},
			'extras': [extra.to_json for extra in self.extras],
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_admin(self):
		return {
			'id': self.pk,
			'number': self.number,
			'token': self.token,
			'amount': self.amount,
			'discount': self.discount,
			'tips': self.tips,
			'extrasTotal': self.extras_total,
			'total': self.total,
			'currency': self.currency,
			'isRequested': self.is_requested,
			'isPaid': self.is_paid,
			'isComplete': self.is_complete,
			'paidBy': self.paid_by,
			'orders': {
				'count': self.orders_count,
				'orders': [order.to_admin_json for order in self.orders]
			},
			'extras': [extra.to_json for extra in self.extras],
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class BillExtra(models.Model):
	bill = models.ForeignKey(Bill, on_delete=models.PROTECT)
	name = models.CharField(max_length=200, null=False, blank=False)
	price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
	quantity = models.IntegerField(null=False, blank=False, default=1)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def total(self):
		return self.price * self.quantity
	
	@property
	def to_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'price': float(self.price),
			'quantity': self.quantity,
			'total': float(self.total),
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}
	

class Placement(models.Model):
	restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
	branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	table = models.ForeignKey(RestaurantTable, on_delete=models.PROTECT)
	booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.PROTECT)
	waiter = models.ForeignKey(Administrator, null=True, blank=True, on_delete=models.PROTECT)
	bill = models.ForeignKey(Bill, null=True, blank=True, on_delete=models.PROTECT)
	token = models.CharField(max_length=200, null=False, blank=False, unique=True)
	people = models.IntegerField(null=False, blank=False)
	is_done = models.BooleanField(default=False)
	need_someone = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json_s,
			'table': self.table.to_json,
			'booking': self.booking.to_json_s if self.booking != None else None,
			'waiter': self.waiter.to_json_s if self.waiter != None else None,
			'bill': self.bill.to_json_s if self.bill != None and self.bill != '' else None,
			'token': self.token,
			'people': int(self.people),
			'isDone': self.is_done,
			'needSomeone': self.need_someone,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_admin_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_admin_json,
			'table': self.table.to_json_admin_s,
			'booking': self.booking.to_json_s if self.booking != None else None,
			'waiter': self.waiter.to_json_s if self.waiter != None else None,
			'bill': self.bill.to_json_s if self.bill != None and self.bill != '' else None,
			'token': self.token,
			'billNumber': self.bill.number if self.bill != None and self.bill != '' else None,
			'people': int(self.people),
			'isDone': self.is_done,
			'needSomeone': self.need_someone,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_admin_json_s(self):
		return {
			'id': self.pk,
			'user': self.user.to_admin_json,
			'table': self.table.to_json_admin_s,
			'booking': self.booking.to_json_s if self.booking != None else None,
			'waiter': self.waiter.to_json_s if self.waiter != None else None,
			'token': self.token,
			'billNumber': self.bill.number if self.bill != None and self.bill != '' else None,
			'people': int(self.people),
			'isDone': self.is_done,
			'needSomeone': self.need_someone,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class PlacementMessage(models.Model):
	placement = models.ForeignKey(Placement, on_delete=models.PROTECT)
	message = models.TextField(null=False, blank=False)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message

	def __unicode__(self):
		return self.message


class Order(models.Model):
	bill = models.ForeignKey(Bill, on_delete=models.PROTECT)
	menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
	token = models.CharField(max_length=200, null=False, blank=False, unique=True)
	quantity = models.IntegerField(default=1)
	price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	currency = models.CharField(max_length=100, null=False, blank=False)
	conditions = models.TextField(null=True, blank=True)
	is_declined = models.BooleanField(default=False)
	reasons = models.TextField(blank=True, null=True)
	is_delivered = models.BooleanField(default=False)
	has_promotion = models.BooleanField(default=False)
	promotion = models.ForeignKey(Promotion, null=True, blank=True, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.bill.number

	def __unicode__(self):
		return self.bill.number

	@property
	def total(self):
		return self.quantity * self.price

	@property
	def to_json(self):
		return {
			'id': self.pk,
			'menu': self.menu.to_json_s,
			'token': self.token,
			'quantity': self.quantity,
			'price': float(self.price),
			'currency': self.currency,
			'conditions': self.conditions,
			'isAccepted': self.is_delivered,
			'isDeclined': self.is_declined,
			'isDelivered': self.is_delivered,
			'reasons': self.reasons,
			'hasPromotion': self.has_promotion,
			'promotion': self.promotion.string_data_json if self.promotion != None else None,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_json_s(self):
		return {
			'id': self.pk,
			'menu': self.menu.name,
			'token': self.token,
			'quantity': self.quantity,
			'price': float(self.price),
			'currency': self.currency,
			'conditions': self.conditions,
			'isAccepted': self.is_delivered,
			'isDeclined': self.is_declined,
			'isDelivered': self.is_delivered,
			'reasons': self.reasons,
			'hasPromotion': self.has_promotion,
			'promotion': self.promotion.string_data_json if self.promotion != None else None,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

	@property
	def to_admin_json_s(self):
		return {
			'id': self.pk,
			'menu': self.menu.to_json_admin,
			'token': self.token,
			'billNumber': self.bill.number,
			'tableNumber': self.bill.placement.table.number,
			'quantity': self.quantity,
			'price': float(self.price),
			'currency': self.currency,
			'conditions': self.conditions,
			'isAccepted': self.is_delivered,
			'isDeclined': self.is_declined,
			'isDelivered': self.is_delivered,
			'people': self.bill.placement.people,
			'reasons': self.reasons,
			'hasPromotion': self.has_promotion,
			'promotion': self.promotion.string_data_json if self.promotion != None else None,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


	@property
	def to_admin_json(self):
		return {
			'id': self.pk,
			'user': self.bill.placement.user.to_data_json,
			'menu': self.menu.to_json_admin,
			'waiter': self.bill.placement.waiter.to_data_json if self.bill.placement.waiter != None else None,
			'token': self.token,
			'billNumber': self.bill.number,
			'tableNumber': self.bill.placement.table.number,
			'quantity': self.quantity,
			'price': float(self.price),
			'currency': self.currency,
			'conditions': self.conditions,
			'isAccepted': self.is_delivered,
			'isDeclined': self.is_declined,
			'isDelivered': self.is_delivered,
			'people': self.bill.placement.people,
			'reasons': self.reasons,
			'hasPromotion': self.has_promotion,
			'promotion': self.promotion.string_data_json if self.promotion != None else None,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}
	

class Moment(models.Model):
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	placement = models.ForeignKey(Placement, null=True, blank=True, on_delete=models.PROTECT)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user

	def __unicode__(self):
		return self.user


class MomentMedia(models.Model):
	moment = models.ForeignKey(Moment, on_delete=models.PROTECT)
	media_type = models.CharField(max_length=100, null=False, blank=False)
	media = models.FileField(upload_to=moment_file_path, null=False, blank=False)
	text = models.CharField(max_length=255, null=True, blank=True)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.moment

	def __unicode__(self):
		return self.moment
