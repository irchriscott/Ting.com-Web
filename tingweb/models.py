# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from tingadmin.models import RestaurantCategory, TingLicenceKey, Permission
from time import time
import ting.utils as utils

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
	return "foods/%s_%s" % (str(time()).replace('.','_'), filename)

def category_image_path(instance, filename):
	return "categories/%s_%s" % (str(time()).replace('.','_'), filename)


### USER RESTAURANT


class Restaurant(models.Model):
	token = models.TextField(null=False, blank=False)
	name = models.CharField(max_length=200, null=False, blank=False)
	motto = models.TextField(null=True, blank=True)
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
	def categories(self):
		return CategoryRestaurant.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def tables(self):
		return RestaurantTable.objects.filter(restaurant=self.pk).order_by('-created_at')

	def tables_count(self):
		return self.tables.count()

	@property
	def administrators(self):
		return Administrator.objects.filter(restaurant=self.pk).order_by('-created_at')

	def administrators_count(self):
		return self.administrators.count()

	def config(self):
		return RestaurantConfig.objects.get(restaurant=self.pk)

	@property
	def likes(self):
		return UserRestaurant.objects.filter(restaurant=self.pk).order_by('-created_at')

	def likes_count(self):
		return self.likes.count()

	@property
	def reviews(self):
		return RestaurantReview.objects.filter(restaurant=self.pk).order_by('created_at')

	def reviews_count(self):
		return self.reviews.count()

	@property
	def food_categories(self):
		return FoodCategory.objects.filter(restaurant=self.pk).order_by('-created_at')

	def food_categories_count(self):
		return self.categories.count()

	@property
	def menus(self):
		return Menu.objects.filter(restaurant=self.pk).order_by('-created_at')

	def menus_count(self):
		return self.menus.count()

	@property
	def foods(self):
		return Food.objects.filter(restaurant=self.pk).order_by('-created_at')

	def foods_count(self):
		return self.foods.count()

	@property
	def appetizers(self):
		return Food.objects.filter(restaurant=self.pk, food_type=1).order_by('-created_at')

	def appetizers_count(self):
		return self.appetizers.count()

	@property
	def meals(self):
		return Food.objects.filter(restaurant=self.pk, food_type=2).order_by('-created_at')

	def meals_count(self):
		return self.meals.count()

	@property
	def desserts(self):
		return Food.objects.filter(restaurant=self.pk, food_type=3).order_by('-created_at')

	def desserts_count(self):
		return self.desserts.count()

	@property
	def sauces(self):
		return Food.objects.filter(restaurant=self.pk, food_type=4).order_by('-created_at')

	def sauces_count(self):
		return self.sauces.count()

	@property
	def drinks(self):
		return Drink.objects.filter(restaurant=self.pk).order_by('-created_at')

	def drinks_count(self):
		return self.drinks.count()

	@property
	def dishes(self):
		return Dish.objects.filter(restaurant=self.pk).order_by('-created_at')

	def dishes_count(self):
		return self.dishes.count()

	@property
	def images(self):
		return RestaurantImage.objects.filter(restaurant=self.pk).order_by('-created_at')

	@property
	def branches(self):
		return Branch.objects.filter(restaurant=self.pk).order_by('created_at')

	def branches_count(self):
		return self.branches.count()

	def to_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'motto': self.motto,
			'categories': {
				'count': self.categories.count(),
				'categories': [category.to_json() for category in self.categories]
			},
			'logo': self.logo,
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
				'count': self.branches.count(),
				'branches': [branch.to_json() for branch in self.branches]
			},
			'images': {
				'count': self.images.count(),
				'images': [image.to_json() for image in self.images]
			},
			'tables': {
				'count': self.tables_count,
				'tables': [table.to_json() for table in self.tables]
			},
			'likes':{
				'count': self.likes_count,
				'likes': [like.to_json() for like in self.likes]
			},
			'reviews': {
				'count': self.reviews_count,
				'reviews': [review.to_json() for review in self.reviews]
			},
			'foodCategories':{
				'count': self.food_categories_count,
				'categories': [category.to_json() for category in self.food_categories]
			},
			'config': self.config.to_json(),
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Branch(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	name = models.CharField(max_length=200, null=False, blank=False)
	country = models.CharField(max_length=200, null=False, blank=False)
	town = models.CharField(max_length=255, null=False, blank=False)
	address = models.TextField(null=False, blank=False)
	latitude = models.CharField(max_length=200, null=False, blank=False)
	longitude = models.CharField(max_length=200, null=False, blank=False)
	place_id = models.CharField(max_length=200, null=False, blank=False)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def tables(self):
		return RestaurantTable.objects.filter(branch=self.pk)

	def tables_count(self):
		return self.tables.count()

	def to_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'country': self.country,
			'town': self.town,
			'address': self.address,
			'latitude': self.latitude,
			'longitude': self.longitude,
			'placeId': self.place_id,
			'tables':{
				'count': self.tables_count(),
				'tables': [table.to_json() for table in self.tables]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class RestaurantImage(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	image = models.ImageField(upload_to=restaurant_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant.name

	def __unicode__(self):
		return self.restaurant.name

	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class CategoryRestaurant(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	category = models.ForeignKey(RestaurantCategory)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant

	def __unicode__(self):
		return self.restaurant

	def to_json(self):
		return {
			'id': self.pk,
			'category': self.category.to_json(),
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class RestaurantTable(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	uuid = models.CharField(max_length=100, null=False, blank=False)
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

	def to_json(self):
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


class Administrator(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	token = models.TextField(null=False, blank=False)
	name = models.CharField(max_length=200, null=False, blank=False)
	username = models.CharField(max_length=100, null=False, blank=False, unique=True)
	email = models.EmailField(null=False, blank=False, unique=True)
	password = models.TextField(null=False, blank=False)
	phone = models.CharField(max_length=15, blank=False, null=False)
	image = models.ImageField(upload_to=administrator_image_path, null=False, blank=False)
	admin_type = models.CharField(max_length=100, null=False, blank=True)
	badge_number = models.CharField(max_length=200, null=True, blank=True)
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

	def to_json(self):
		return {
			'id': self.pk,
			'branch': self.branch.to_json(),
			'name': self.name,
			'username': self.username,
			'type': self.admin_type_str,
			'email': self.email,
			'phone': self.phone,
			'image': self.image,
			'badgeNumber': self.badge_number,
			'permissions': self.permissions,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}



class AdministratorResetPassword(models.Model):
	admin = models.ForeignKey(Administrator)
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
	admin = models.OneToOneField(Administrator)
	permissions = models.TextField(null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.admin

	def __unicode__(self):
		return self.admin


class RestaurantConfig(models.Model):
	restaurant = models.OneToOneField(Restaurant)
	admin = models.ForeignKey(Administrator, null=True, blank=True)
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
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.restaurant.name

	def __unicode__(self):
		return self.restaurant.name

	def to_json(self):
		return {
			'id': self.pk,
			'currency': self.currency,
			'tax': self.tax,
			'email': self.email,
			'cancelLateBooking': self.cancel_late_booking
		}


class RestaurantLicenceKey(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	key = models.ForeignKey(TingLicenceKey)
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
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def categories(self):
		return UserCategory.objects.filter(user=self.pk).order_by('-created_at')

	def categories_count(self):
		return self.categories.count()

	@property
	def restaurants(self):
		return UserRestaurant.objects.filter(user=self.pk).order_by('-created_at')

	def restaurants_count(self):
		return self.restaurants.count()

	@property
	def restaurant_reviews(self):
		return RestaurantReview.objects.filter(user=self.pk).order_by('-created_at')

	def restaurant_reviews_count(self):
		return self.reviews.count()

	@property
	def menu_reviews(self):
		return MenuReview.objects.filter(user=self.pk).order_by('-created_at')

	def menu_reviews_count(self):
		return self.menu_reviews.count()

	@property
	def bookings(self):
		return Booking.objects.filter(user=self.pk).order_by('-created_at')

	def bookings_count(self):
		return self.bookings.count()

	@property
	def placements(self):
		return Placement.objects.filter(user=self.pk).order_by('-created_at')

	def placements_count(self):
		return self.placements.count()

	@property
	def addresses(self):
		return UserAddress.objects.filter(user=self.pk).order_by('-created_at')

	def addresses_count(self):
		return self.addresses.count()

	def to_json(self):
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
			'addresses': {
				'count': self.addresses_count,
				'addresses': [address.to_json() for address in self.addresses]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class UserAddress(models.Model):
	user = models.ForeignKey(User)
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
	user = models.ForeignKey(User)
	category = models.ForeignKey(RestaurantCategory)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json(),
			'category': self.category.to_json(),
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

class UserRestaurant(models.Model):
	user = models.ForeignKey(User)
	restaurant = models.ForeignKey(Restaurant)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json(),
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

class RestaurantReview(models.Model):
	user = models.ForeignKey(User)
	restaurant = models.ForeignKey(Restaurant)
	review = models.IntegerField(null=False, blank=False)
	comment = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json(),
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


### MENU AND FOOD


class FoodCategory(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	admin = models.ForeignKey(Administrator)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	description = models.TextField(blank=True, null=True)
	image = models.ImageField(upload_to=category_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

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

	def to_json(self):
		return {
			'id': self.pk,
			'name': self.name,
			'description': self.description,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

class Food(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	admin = models.ForeignKey(Administrator)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	category = models.ForeignKey(FoodCategory)
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

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def type_str(self):
		return utils.get_from_tuple(utils.FOOD_TYPE, self.food_type)

	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=1, menu_id=self.pk)

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	def reviews_count(self):
		return self.reviews.count()

	@property
	def images(self):
		return FoodImage.objects.filter(food=self.pk).order_by('created_at')

	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json(),
			'branch': self.branch.to_json(),
			'name': self.name,
			'category': self.category.to_json(),
			'foodType': utils.get_from_tuple(utils.FOOD_TYPE, self.food_type),
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'reviews': {
				'count': self.reviews_count,
				'reviews': [review.to_json() for review in self.reviews]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json() for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}

class FoodImage(models.Model):
	food = models.ForeignKey(Food)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.food

	def __unicode__(self):
		return self.food

	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}

class Drink(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	admin = models.ForeignKey(Administrator)
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

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def type_str(self):
		return utils.get_from_tuple(utils.DRINK_TYPE, self.drink_type)

	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=2, menu_id=self.pk)

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	def reviews_count(self):
		return self.reviews.count()

	@property
	def images(self):
		return DrinkImage.objects.filter(drink=self.pk).order_by('-created_at')

	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json(),
			'branch': self.branch.to_json(),
			'name': self.name,
			'drinkType': self.drink_type_str,
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'reviews': {
				'count': self.reviews_count,
				'reviews': [review.to_json() for review in self.reviews]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json() for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class DrinkImage(models.Model):
	drink = models.ForeignKey(Drink)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.drink

	def __unicode__(self):
		return self.drink

	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Dish(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	admin = models.ForeignKey(Administrator)
	name = models.CharField(max_length=250, null=False, blank=False)
	slug = models.CharField(max_length=250, null=False, blank=False)
	category = models.ForeignKey(FoodCategory)
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
	drink = models.ForeignKey(Drink, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	@property
	def dish_time_str(self):
		return utils.get_from_tuple(utils.DISH_TIME, self.dish_time)

	def menu(self):
		return Menu.objects.get(restaurant=self.restaurant.pk, menu_type=3, menu_id=self.pk)

	@property
	def foods(self):
		return DishFood.objects.filter(dish=self.pk).order_by('-created_at')

	@property
	def foods_ids(self):
		return [food.food.id for food in self.foods]

	def foods_count(self):
		return self.foods.count()

	@property
	def reviews(self):
		return MenuReview.objects.filter(menu=self.menu.pk).order_by('-created_at')

	def reviews_count(self):
		return self.reviews.count()

	@property
	def images(self):
		return DishImage.objects.filter(dish=self.pk).order_by('-created_at')

	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json(),
			'branch': self.branch.to_json(),
			'name': self.name,
			'category': self.category.to_json(),
			'dishTime': self.dish_time, # To Be Fixed
			'description': self.description,
			'ingredients': self.ingredients,
			'showIngredients': self.show_ingredients,
			'price': self.price,
			'lastPrice': self.last_price,
			'currency': self.currency,
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'hasDrink': self.has_drink,
			'drink': self.drink.to_json(),
			'reviews': {
				'count': self.reviews_count,
				'reviews': [review.to_json() for review in self.reviews]
			},
			'foods': {
				'count': self.foods,
				'foods': [food.to_json() for food in self.foods]
			},
			'images':{
				'count': self.images.count(),
				'images': [image.to_json() for image in self.images]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class DishImage(models.Model):
	dish = models.ForeignKey(Dish)
	image = models.ImageField(upload_to=food_image_path, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.dish

	def __unicode__(self):
		return self.dish

	def to_json(self):
		return {
			'id': self.pk,
			'image': self.image,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class DishFood(models.Model):
	dish = models.ForeignKey(Dish)
	food = models.ForeignKey(Food)
	is_countable = models.BooleanField(default=False)
	quantity = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.food.name

	def __unicode__(self):
		return self.food.name

	def to_json(self):
		return {
			'id': self.pk,
			'food': self.food.to_json(),
			'isCountable': self.is_countable,
			'quantity': self.quantity,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Menu(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	admin = models.ForeignKey(Administrator)
	menu_type = models.IntegerField(null=False, blank=False)
	menu_id = models.IntegerField(null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.menu_type

	def __unicode__(self):
		return self.menu_type

	def menu(self):
		if self.menu_type == 1:
			return Food.objects.get(pk=self.menu_id)
		elif self.menu_type == 2:
			return Drink.objects.get(pk=self.menu_id)
		elif self.menu_type == 3:
			return Dish.objects.get(pk=self.menu_id)

	def to_json(self):
		return {
			'type':{
				'id': self.menu_type,
				'name': utils.get_from_tuple(utils.MENU_TYPE, self.menu_type)
			},
			'menu': menu.to_json()
		}


class MenuReview(models.Model):
	user = models.ForeignKey(User)
	menu = models.ForeignKey(Menu)
	review = models.IntegerField(null=False, blank=False)
	comment = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json(),
			'review': self.review,
			'comment': self.comment,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Promotion(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	admin = models.ForeignKey(Administrator)
	uuid = models.CharField(max_length=100, null=False, blank=False)
	occasion_event = models.CharField(max_length=200, null=False, blank=False)
	promotion_menu_type = models.CharField(max_length=100, null=False, blank=False)
	menu = models.ForeignKey(Menu, null=True, blank=True, related_name='menu')
	has_reduction = models.BooleanField(default=True)
	amount = models.IntegerField(null=True, blank=True, default=0)
	reduction_type = models.CharField(max_length=100, null=True, blank=True) # Currency Or %
	has_supplement = models.BooleanField(default=False)
	supplement_max_quantity = models.IntegerField(default=1, null=False, blank=False)
	is_supplement_same = models.BooleanField(default=False)
	supplement = models.ForeignKey(Menu, null=True, blank=True, related_name='supplement')
	supplement_quantity = models.IntegerField(default=1, null=False, blank=False)
	is_on = models.BooleanField(default=True)
	start_date = models.DateField(null=False, blank=False)
	end_date = models.DateField(null=False, blank=False)
	description = models.TextField(null=False, blank=False)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.occasion_event

	def __unicode__(self):
		return self.occasion_event

	@property
	def interests(self):
		return PromotionInterest.objects.filter(promotion=self.pk)

	def interests_count(self):
		return self.interests.count()

	def to_json(self):
		return {
			'id': self.pk
		}
	


class PromotionInterest(models.Model):
	promotion = models.ForeignKey(Promotion)
	user = models.ForeignKey(User)
	is_interested = models.BooleanField(default=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.promotion.occasion_event

	def __unicode__(self):
		return self.promotion.occasion_event

	def to_json(self):
		return {
			'id': self.pk,
			'user': self.user.to_json(),
			'isInterested': self.is_interested
		}




### BOOK, ORDERS, BILLS


class Booking(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	user = models.ForeignKey(User)
	table = models.ForeignKey(RestaurantTable)
	token = models.CharField(max_length=100, null=False, blank=False)
	people = models.IntegerField(null=False, blank=False)
	date = models.DateField(null=False, blank=False)
	time = models.TimeField(null=False, blank=False)
	is_complete = models.BooleanField(default=False)
	is_canceled = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json(),
			'branch': self.branch.to_json(),
			'user': self.user.to_json(),
			'table': self.table.to_json(),
			'token': self.token,
			'people': self.people,
			'date': self.date,
			'time': self.time,
			'isComplete': self.is_complete,
			'isCanceled': self.is_canceled,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Placement(models.Model):
	restaurant = models.ForeignKey(Restaurant)
	branch = models.ForeignKey(Branch)
	user = models.ForeignKey(User)
	table = models.ForeignKey(RestaurantTable)
	booking = models.ForeignKey(Booking, null=True, blank=True)
	waiter = models.ForeignKey(Administrator, null=True, blank=True)
	token = models.CharField(max_length=100, null=False, blank=False)
	people = models.IntegerField(null=False, blank=False)
	is_done = models.BooleanField(default=False)
	need_someone = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.name

	def __unicode__(self):
		return self.user.name

	def bills(self):
		return Bill.objects.filter(placement=self.pk).order_by('-created_at')

	def bill(self):
		return Bill.objects.get(placement=self.pk)

	def to_json(self):
		return {
			'id': self.pk,
			'restaurant': self.restaurant.to_json(),
			'branch': self.branch.to_json(),
			'user': self.user.to_json(),
			'table': self.table.to_json(),
			'booking': self.booking.to_json(),
			'waiter': self.waiter.to_json(),
			'bill': self.bill.to_json(),
			'token': self.token,
			'people': self.people,
			'isDone': self.is_done,
			'needSomeone': self.need_someone,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Bill(models.Model):
	placement = models.OneToOneField(Placement)
	admin = models.ForeignKey(Administrator)
	number = models.CharField(max_length=20, null=False, blank=False)
	token = models.CharField(max_length=100, null=False, blank=False)
	amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
	discount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
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

	def orders(self):
		return Order.objects.filter(bill=self.pk).order_by('-created_at')

	def orders_count(self):
		return self.orders.count()

	def to_json(self):
		return {
			'id': self.pk,
			'admin': self.admin.to_json(),
			'number': self.number,
			'token': self.token,
			'amount': self.amount,
			'discount': self.discount,
			'currency': self.currency,
			'isRequested': self.is_requested,
			'isPaid': self.is_paid,
			'isComplete': self.is_complete,
			'paidBy': self.paid_by,
			'orders': {
				'count': self.orders_count,
				'orders': [order.to_json() for order in self.orders]
			},
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}


class Order(models.Model):
	bill = models.ForeignKey(Bill)
	menu = models.ForeignKey(Menu)
	token = models.CharField(max_length=100, null=False, blank=False)
	quantity = models.IntegerField(default=1)
	price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
	currency = models.CharField(max_length=100, null=False, blank=False)
	is_declined = models.BooleanField(default=False)
	reasons = models.TextField(blank=True, null=True)
	is_delivered = models.BooleanField(default=False)
	has_promotion = models.BooleanField(default=False)
	promotion = models.ForeignKey(Promotion, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.bill.number

	def __unicode__(self):
		return self.bill.number

	def to_json(self):
		return {
			'id': self.pk,
			'menu': self.menu.to_json(),
			'token': self.token,
			'quantity': self.quantity,
			'price': self.price,
			'currency': self.currency,
			'isDeclined': self.is_declined,
			'reasons': self.reasons,
			'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
		}