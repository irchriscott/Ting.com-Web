from django import template
from tingweb.models import Administrator, DishFood
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