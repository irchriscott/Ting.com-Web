from __future__ import unicode_literals

TING_PACKAGES = (
		(1, 'Trial'),
		(2, 'Silver'),
		(3, 'Gold'),
		(4, 'Platinum')
	)

ADMIN_TYPE = (
		(1, 'Administrator'),
		(2, 'Supervisor'),
		(3, 'Chef'),
		(4, 'Waiter'),
		(5, 'Accountant')
	)

GENDER = (
		('male', 'Male'),
		('female', 'Female')
	)

MENU_TYPE = (
		(1, 'Food'),
		(2, 'Drink'),
		(3, 'Dish')
	)

FOOD_TYPE = (
		(1, 'Appetizer'),
		(2, 'Meal'),
		(3, 'Dessert'),
		(4, 'Sauce')
	)

DRINK_TYPE = (
		(1, 'Water'),
		(2, 'Beverage (Tea, Coffee, Milk, Late)'),
		(3, 'Beer'),
		(4, 'Alcohol'),
		(5, 'Soda'),
		(6, 'Juice'),
		(7, 'Smoothie'),
		(8, 'Cocktail'),
		(9, 'Wine'),
		(10, 'Other')
	)

DISH_TIME = (
		(1, 'Breakfast'),
		(2, 'Lunch'),
		(3, 'Dinner'),
		(4, 'Supper'),
		(5, 'Snack'),
		(6, 'Other')
	)

PAID_BY = (
		(1, 'Cash'),
		(2, 'Mobile Money'),
		(3, 'Credit Card')
	)


CURRENCIES = (
		('USD', 'United State Dollar'),
		('UGX', 'Ugandan Shillings'),
		('GBP', 'Grand Britain Pounds')
	)


def get_from_tuple(data, key):
	if isinstance(data, tuple) is True:
		for t in data:
			if isinstance(t, tuple) is True:
				try:
					if int(t[0]) == int(key):
						return t[1]
				except Exception:
					for i in t:
						if key in i:
							return t[1] if str(t[0]) == str(key) else key
	return key

DEFAULT_USER_IMAGE = 'users/default.jpg'

DEFAULT_ADMIN_IMAGE = 'administrators/default.jpg'

DEFAULT_RESTAURANT_IMAGE = 'restaurants/default.jpg'

DEFAULT_ADMIN_NAME = 'Restaurant Admin'

DEFAULT_ADMIN_USERNAME = 'admin'