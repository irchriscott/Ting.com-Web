from django import template
from tingweb.models import Administrator, DishFood, Menu, Food, Dish, Drink
import ting.utils as utils

register = template.Library()


@register.filter(name='lower')
def lower(value):
	return value.lower()


@register.filter(name='upper')
def upper(value):
	return value.upper()


@register.filter(name='yesno')
def yes_no(value):
	if value is True:
		return 'Yes'
	elif value is False:
		return 'No'
	else:
		return value


@register.filter(name='none')
def no_none(value):
	return '' if value is None else value


@register.filter(name='to_str')
def to_str(value):
	return str(value)


@register.filter(name='to_int')
def to_int(value):
	try:
		return int(value)
	except Exception as e:
		return value


@register.filter(name='has_p')
def has_permission(value, arg):
	admin = Administrator.objects.get(pk=value)
	return admin.has_permission(arg)


@register.filter(name='prefix')
def prefix(value, arg):
	return '{0} {1}'.format(arg, value)


@register.filter(name='from_t')
def from_tupple(value, arg):
	return utils.get_from_tuple(arg, value)

@register.filter(name='dish_food_q')
def dish_food_quantity(value, arg):
	food = DishFood.objects.filter(food=int(value), dish=int(arg)).last()
	return food.quantity

@register.filter(name='menu_name')
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

@register.filter(name='menu_image')
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

@register.filter(name='menu_type')
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