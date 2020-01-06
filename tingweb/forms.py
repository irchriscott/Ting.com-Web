from __future__ import unicode_literals
from django import forms
from tingweb.models import (
							Restaurant, RestaurantConfig, Administrator, Food, Drink, Dish, FoodImage,
							FoodCategory, DrinkImage, DishImage, Branch, RestaurantTable, Promotion,
							User, UserAddress, MenuReview, RestaurantReview, Booking
						)


# RESTAURANT FORMS


class RestaurantUpdateLogo(forms.ModelForm):

	class Meta:
		model = Restaurant
		fields = ('logo',)


class RestaurantUpdateProfile(forms.ModelForm):

	class Meta:
		model = Restaurant
		fields = ('name', 'motto', 'opening', 'closing',)


class RestaurantUpdateConfig(forms.ModelForm):

	class Meta:
		model = RestaurantConfig
		fields = ('currency', 'use_default_currency', 'tax', 
					'cancel_late_booking', 'waiter_see_all_orders', 'book_with_advance', 
					'booking_advance', 'booking_cancelation_refund', 'booking_cancelation_refund_percent', 
					'booking_payement_mode', 'days_before_reservation', 'can_take_away', 'user_should_pay_before')


class AddNewBranch(forms.ModelForm):

	class Meta:
		model = Branch
		fields = ('name', 'country', 'town', 'address', 'longitude', 'latitude', 'place_id', 'email', 'phone', 'region', 'road')


class UpdateBranchProfile(forms.ModelForm):

	class Meta:
		model = Branch
		fields = ('name', 'email', 'phone', 'region', 'road')


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


class AddMenuDrink(forms.ModelForm):

	class Meta:
		model = Drink
		fields = ('name', 'drink_type', 'description', 'ingredients', 'price', 'last_price', 'currency')


class DrinkImageForm(forms.ModelForm):

	class Meta:
		model = DrinkImage
		fields = ('image',)


class EditMenuDrink(forms.ModelForm):

	class Meta:
		model = Drink
		fields = ('name', 'description', 'ingredients', 'price', 'last_price', 'currency')


class AddMenuDish(forms.ModelForm):

	class Meta:
		model = Dish
		fields = ('name', 'dish_time', 'description', 'ingredients', 'price', 'last_price', 'currency')


class DishImageForm(forms.ModelForm):

	class Meta:
		model = DishImage
		fields = ('image',)


class EditMenuDish(forms.ModelForm):

	class Meta:
		model = Dish
		fields = ('name', 'description', 'ingredients', 'price', 'last_price', 'currency')


class RestaurantTableForm(forms.ModelForm):

	class Meta:
		model = RestaurantTable
		fields = ('number', 'max_people', 'location', 'chair_type', 'description')


class PromotionForm(forms.ModelForm):

	class Meta:
		model = Promotion
		fields = ('occasion_event', 'promotion_menu_type', 'poster_image', 'description')


class PromotionEditForm(forms.ModelForm):

	class Meta:
		model = Promotion
		fields = ('occasion_event', 'description')



# USER FORMS


class GoogleSignUpForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('name', 'email', 'token', 'country', 'town')


class EmailSignUpForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('email', 'name', 'username', 'country', 'town', 'gender', 'date_of_birth')


class UserLocationForm(forms.ModelForm):

	class Meta:
		model = UserAddress
		fields = ('address', 'longitude', 'latitude', 'type')


class UserImageForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('image',)


class MenuReviewForm(forms.ModelForm):

	class Meta:
		model = MenuReview
		fields = ('review', 'comment')


class RestaurantReviewForm(forms.ModelForm):

	class Meta:
		model = RestaurantReview
		fields = ('review', 'comment')


class ReservationForm(forms.ModelForm):

	class Meta:
		model =  Booking
		fields = ('people', 'location', 'date')