from __future__ import unicode_literals
from django import forms
from tingweb.models import (
							Restaurant, RestaurantConfig, Administrator, Food, Drink, Dish, FoodImage,
							FoodCategory
						)


class RestaurantUpdateLogo(forms.ModelForm):

	class Meta:
		model = Restaurant
		fields = ('logo',)


class RestaurantUpdateProfile(forms.ModelForm):

	class Meta:
		model = Restaurant
		fields = ('name', 'branch', 'motto', 'opening', 'closing',)


class RestaurantUpdateConfig(forms.ModelForm):

	class Meta:
		model = RestaurantConfig
		fields = ('currency', 'use_default_currency', 'tax', 'cancel_late_booking', 'waiter_see_all_orders', 'book_with_advance', 'booking_advance',)


class AddAdministrator(forms.ModelForm):

	class Meta:
		model = Administrator
		fields = ('name', 'username', 'email', 'phone', 'badge_number', 'admin_type',)


class AdministratorUpdateImage(forms.ModelForm):

	class Meta:
		model = Administrator
		fields = ('image',)


class AdministratorUpdateProfile(forms.ModelForm):

	class Meta:
		model = Administrator
		fields = ('name', 'phone', 'badge_number', 'admin_type',)


class AdministratorUpdateUsername(forms.ModelForm):

	class Meta:
		model = Administrator
		fields = ('username',)


class AdministratorUpdateEmail(forms.ModelForm):

	class Meta:
		model = Administrator
		fields = ('email',)


class FoodCategoryForm(forms.ModelForm):

	class Meta:
		model = FoodCategory
		fields = ('name', 'description', 'image')


class EditFoodCategoryForm(forms.ModelForm):

	class Meta:
		model = FoodCategory
		fields = ('name', 'description',)


class AddMenuFood(forms.ModelForm):

	class Meta:
		model = Food
		fields = ('name', 'food_type', 'description', 'ingredients', 'price', 'last_price', 'currency')


class EditMenuFood(forms.ModelForm):

	class Meta:
		model = Food
		fields = ('name', 'description', 'ingredients', 'price', 'last_price', 'currency')


class FoodImageForm(forms.ModelForm):

	class Meta:
		model = FoodImage
		fields = ('image',)