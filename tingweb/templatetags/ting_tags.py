from django import template
from tingweb.models import (
								Administrator, DishFood, Menu, Food, Dish, Drink, FoodCategory, 
								Branch, Restaurant, Promotion
							)
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


@register.filter(name='has_s')
def has_special(value, arg):
	branch = Branch.objects.get(pk=value)
	return branch.has_special(arg)


@register.filter(name='has_serv')
def has_service(value, arg):
	branch = Branch.objects.get(pk=value)
	return branch.has_service(arg)


@register.filter(name='has_category')
def has_category(value, arg):
	resto = Restaurant.objects.get(pk=value)
	return resto.has_category(arg)


@register.filter(name='has_interest')
def has_interest(value, arg):
	promo = Promotion.objects.get(pk=value)
	return promo.has_user_interest(arg)


@register.filter(name='has_liked')
def has_liked(value, arg):
	branch = Branch.objects.get(pk=int(value))
	return branch.has_liked(arg)


@register.filter(name='has_liked_menu')
def has_liked_menu(value, arg):
	menu = Menu.objects.get(pk=value)
	return menu.has_liked(arg)


@register.filter(name='prefix')
def prefix(value, arg):
	return '{0} {1}'.format(arg, value)


@register.filter(name='from_t')
def from_tupple(value, arg):
	return utils.get_from_tuple(arg, value)


@register.filter(name='to_slug')
def to_slug(value):
	return value.lower().replace(' ', '-')


@register.filter(name='from_slug')
def from_slug(value):
	return value.replace('-', '')


@register.filter(name='dish_food_q')
def dish_food_quantity(value, arg):
	food = DishFood.objects.filter(food=int(value), dish=int(arg)).last()
	return food.quantity


@register.filter(name='rand_five_all')
def random_five_menu_all(value):
	menus = Menu.objects.filter(branch__pk=value)
	return menus.random(5)


@register.filter(name='rand_five_all_count')
def random_five_menu_all_count(value):
	menus = Menu.objects.filter(branch__pk=value)
	return menus.count()


@register.filter(name='rand_five_type')
def random_five_menu_type(value, arg):
	menus = Menu.objects.filter(branch__pk=value, menu_type=arg)
	return menus.random(5)


@register.filter(name='rand_five_type_count')
def random_five_menu_type_count(value, arg):
	menus = Menu.objects.filter(branch__pk=value, menu_type=arg)
	return menus.count()


@register.filter(name='rand_five_category')
def random_five_menu_category(value, arg):
	menus = Menu.objects.filter(branch__pk=value)
	return [menu for menu in menus if menu.menu_type != 2 and menu.to_json['menu']['category']['id'] == arg]


@register.filter(name='rand_five_category_count')
def random_five_menu_category_count(value, arg):
	menus = Menu.objects.filter(branch__pk=value)
	return len([menu for menu in menus if menu.menu_type != 2 and menu.to_json['menu']['category']['id'] == arg])


@register.filter(name='category_menus_count')
def category_menus_count(value, arg):
	dishes = Dish.objects.filter(category__pk=arg, branch__pk=value).count()
	foods = Food.objects.filter(category__pk=arg, branch__pk=value).count()
	return dishes + foods


@register.filter(name='cuisine_menus_count')
def cuisine_menus_count(value, arg):
	dishes = Dish.objects.filter(cuisine__pk=arg, branch__pk=value).count()
	foods = Food.objects.filter(cuisine__pk=arg, branch__pk=value).count()
	return dishes + foods


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